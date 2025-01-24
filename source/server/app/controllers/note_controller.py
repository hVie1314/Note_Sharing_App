from flask import jsonify, request
from werkzeug.utils import secure_filename  # Thêm import này
from config import Config
from app.models.models import Note, SharedUrl, User
from app import db
from datetime import datetime, timedelta
import os
import pytz

def create_note(data):
    try:
        filename = secure_filename(data['filename'])
        file_path = os.path.join('./app/uploads', filename)
        
        new_note = Note(
            filename=filename,
            file_path=file_path,
            username=request.form.get('username')
        )
        db.session.add(new_note)
        db.session.commit()

        return jsonify({"message": "Note created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def upload_file(data):
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
            
        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)

        # Check if file already exists and rename if necessary
        base, extension = os.path.splitext(filename)
        counter = 1
        while os.path.exists(file_path):
            filename = f"{base}({counter}){extension}"
            file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            counter += 1
        
        # Create directory if it doesn't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Save file
        file.save(file_path)
        
        # Lưu vào database
        new_note = Note(
            filename=filename,
            file_path=file_path,
            username=request.form.get('username')
        )
        
        db.session.add(new_note)
        db.session.commit()
        
        return jsonify({
            "message": "File uploaded successfully",
            "file_path": file_path
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def fetch_note(note_id):
    try:
        note = Note.query.get(note_id)
        if not note:
            return jsonify({"error": "Note not found"}), 404

        # Đọc nội dung file từ đường dẫn
        with open(note.file_path, 'rb') as f:
            file_content = f.read()

        return jsonify({
            "filename": note.filename,
            "content": file_content
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def share_note(data):
    try:
        note_id = data.get('note_id')
        expires_days = int(data.get('expires_days', 0)) 
        expires_hours = int(data.get('expires_hours',0))
        expires_minutes = int(data.get('expires_minutes',0));
        key = data.get('user_key') 
        # Get current user
        token = request.headers.get('Authorization').split(" ")[1]
        current_user = User.query.filter_by(token=token).first()
        if not current_user:
            return jsonify({"error": "User not found"}), 404

        # Get note
        note = Note.query.get(note_id)
        if not note:
            return jsonify({"error": "Note not found"}), 404

        vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        # Lấy thời gian hiện tại theo múi giờ Việt Nam
        current_time = datetime.now(vietnam_tz)

        # Calculate expiry date
        expires_at = current_time + timedelta(days=expires_days, hours=expires_hours, minutes=expires_minutes)
        # Create share URL
        shared_url = SharedUrl(
            note_id=note_id,
            username=current_user.username,
            expires_at=expires_at,
            user_key=key
        )
        db.session.add(shared_url)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Note shared successfully",
            "share_url": f"{shared_url.url}"
        }), 200
        
    except Exception as e:
        print(f"Share note error: {str(e)}")  # Debug log
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def access_shared_note(data):
    try:
        # Kiểm tra URL chia sẻ
        temp_url = data.get('url_id')
        shared_note = SharedUrl.query.filter_by(url=temp_url).first()
        if not shared_note:
            return jsonify({"error": "Shared note not found"}), 404

        # Lấy thời gian hiện tại theo múi giờ Việt Nam
        current_time = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
        expires_at_aware = shared_note.expires_at.replace(tzinfo=pytz.FixedOffset(7 * 60))
        # Kiểm tra thời gian hết hạn
        
        if current_time > expires_at_aware:
            return jsonify({
                "success": False,
                "error": "URL đã hết hạn"
            }), 403
        # Lấy note từ database
        note = Note.query.get(shared_note.note_id)
        if not note:
            return jsonify({"error": "Note not found"}), 404

        # Trả về thông tin note và nội dung đã mã hóa
        rs = {
            'id': note.id,
            'filename': note.filename
        }
        return jsonify({
            "success": True,
            "notes": rs  # Danh sách files đã upload
        }), 200
        
    except Exception as e:
        print(e);
        return jsonify({"error": str(e)}), 500


def fetch_user_notes():
    try:
        token = request.headers.get('Authorization').split(" ")[1]
        user = User.query.filter_by(token=token).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        # Lấy danh sách files đã upload của user
        notes = Note.query.filter_by(username=user.username).all()
        
        notes_list = [{
            'id': note.id,
            'filename': note.filename
        } for note in notes]
        
        return jsonify({
            "success": True,
            "notes": notes_list  # Danh sách files đã upload
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
def delete_note(note_id):
    try:
        # Lấy token từ header
        token = request.headers.get('Authorization').split(" ")[1]
        user = User.query.filter_by(token=token).first()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        # Tìm note cần xóa
        note = Note.query.get(note_id)
        
        if not note:
            return jsonify({"error": "Note not found"}), 404
            
        # Kiểm tra quyền sở hữu
        if note.username != user.username:
            return jsonify({"error": "Unauthorized"}), 403
            
        # Xóa file vật lý
        if os.path.exists(note.file_path):
            os.remove(note.file_path)
            
        # Xóa record trong database
        db.session.delete(note)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Note deleted successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
def get_shared_urls_by_user(username):
    """Lấy danh sách URLs được chia sẻ cho user"""
    try:
        shared_urls = SharedUrl.query.filter_by(username=username).all()
        urls_list = []
        current_time = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

        for shared_url in shared_urls:
            # Kiểm tra thời gian hết hạn
            expires_at_aware = shared_url.expires_at.replace(tzinfo=pytz.FixedOffset(7 * 60))
            print(current_time, expires_at_aware)
            if current_time <= expires_at_aware:   
                urls_list.append({
                        'url': shared_url.url,
                        'expires_at': shared_url.expires_at.strftime("%Y-%m-%d %H:%M"),
                        'shared_by': shared_url.note.username
                    })
        return jsonify({
            "success": True,
            "shared_urls": urls_list
        }), 200
    except Exception as e:
        print(e);
        return jsonify({"error": str(e)}), 500