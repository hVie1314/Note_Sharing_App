from flask import jsonify, request
from werkzeug.utils import secure_filename  # Thêm import này
from config import Config
from app.models.models import Note, SharedUrl, User
from app.utils.encryption import encrypt_note, decrypt_note
from app import db
from datetime import datetime
import os

def create_note(data):
    try:
        note_content = data['content']
        password = data['password']
        expires_at = data.get('expires_at', None)

        encrypted_note = encrypt_note(note_content, password)
        new_note = Note(
            content=encrypted_note['content'],
            encryption_key=password,
            expires_at=expires_at,
            username=request.form.get('username'),
            iv=encrypted_note['iv']
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
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        
        # Lưu file
        file.save(file_path)
        
        # Lưu vào database
        new_note = Note(
            filename=filename,
            file_path=file_path,
            encryption_key="default_key",  # Có thể thêm key từ request
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

        password = request.args.get('password')
        if not password:
            return jsonify({"error": "Password is required"}), 400

        encrypted_note = {
            "ciphertext": note.content,
            "iv": note.iv
        }
        decrypted_note = decrypt_note(encrypted_note, password)

        return jsonify({"note": decrypted_note}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def share_note(data):
    try:
        note_id = data['note_id']
        username = data['username']

        note = Note.query.get(note_id)
        if not note:
            return jsonify({"error": "Note not found"}), 404

        if note.expires_at and datetime.utcnow() > note.expires_at:
            return jsonify({"error": "Note has expired"}), 400

        shared_url = SharedUrl(note_id=note_id, username=username, shared_at=datetime.utcnow())
        db.session.add(shared_url)
        db.session.commit()

        return jsonify({"message": "Note shared successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def access_shared_note():
    try:
        temp_url = request.args.get('temp_url')
        shared_note = SharedUrl.query.filter_by(temp_url=temp_url).first()
        if not shared_note:
            return jsonify({"error": "Shared note not found"}), 404

        note = Note.query.get(shared_note.note_id)
        if not note:
            return jsonify({"error": "Note not found"}), 404

        decrypted_note = decrypt_note(note.content, shared_note.password, note.iv)

        return jsonify({"note": decrypted_note}), 200
    except Exception as e:
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