from flask import request, jsonify, Blueprint
from app.models.models import Note
from app.utils.decorators import token_required
from app.models.models import SharedUrl
from app import db
from client.utils.encryption import encrypt_note, decrypt_note
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from config import Config

notes = Blueprint('notes', __name__)

# Route tạo ghi chú mới, mã hóa nội dung ghi chú trước khi lưu
@notes.route('/notes/create', methods=['POST'])
@token_required
def create_note():
    try:
        # Lấy thông tin từ yêu cầu
        data = request.json
        note_content = data['content']
        password = data['password']  # Mật khẩu để mã hóa ghi chú
        expires_at = data.get('expires_at', None)

        # Mã hóa ghi chú trước khi lưu
        encrypted_note = encrypt_note(note_content, password)

        # Lưu ghi chú đã mã hóa vào cơ sở dữ liệu
        new_note = Note(
            content=encrypted_note['content'],  # Ghi chú đã mã hóa
            encryption_key=password,  # Lưu mật khẩu mã hóa
            expires_at=expires_at,
            username=request.form.get('username'),
            iv=encrypted_note['iv']  # Lưu IV để giải mã
        )
        db.session.add(new_note)
        db.session.commit()

        return jsonify({"message": "Note created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route upload file, mã hóa nội dung file trước khi lưu
@notes.route('/notes/upload', methods=['POST'])
@token_required
def create_note():
    try:
        # Lấy thông tin từ yêu cầu
        data = request.json
        note_content = data['content']
        password = data['password']  # Mật khẩu để mã hóa ghi chú
        expires_at = data.get('expires_at', None)

        # Mã hóa ghi chú trước khi lưu
        encrypted_note = encrypt_note(note_content, password)

        # Lưu ghi chú đã mã hóa vào cơ sở dữ liệu
        new_note = Note(
            content=encrypted_note['ciphertext'],  # Ghi chú đã mã hóa
            encryption_key=password,  # Lưu mật khẩu mã hóa
            expires_at=expires_at,
            username=request.form.get('username'),
            iv=encrypted_note['iv']  # Lưu IV để giải mã
        )
        db.session.add(new_note)
        db.session.commit()

        return jsonify({"message": "Note created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route truy xuất ghi chú, giải mã nếu mật khẩu đúng
@notes.route('/notes/<int:note_id>', methods=['GET'])
@token_required
def fetch_note(note_id):
    try:
        note = Note.query.get(note_id)
        if not note:
            return jsonify({"error": "Note not found"}), 404

        password = request.args.get('password')  # Mật khẩu dùng để giải mã
        if not password:
            return jsonify({"error": "Password is required"}), 400

        # Giải mã ghi chú nếu có mật khẩu
        encrypted_note = {
            "ciphertext": note.content,
            "iv": note.iv
        }
        decrypted_note = decrypt_note(encrypted_note, password)

        return jsonify({"note": decrypted_note}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route để chia sẻ ghi chú
@notes.route('/notes/share', methods=['POST'])
@token_required
def share_note():
    try:
        data = request.json
        note_id = data['note_id']
        username = data['username']

        note = Note.query.get(note_id)
        if not note:
            return jsonify({"error": "Note not found"}), 404

        # Kiểm tra nếu ghi chú có hết hạn hay không
        if note.expires_at and datetime.utcnow() > note.expires_at:
            return jsonify({"error": "Note has expired"}), 400

        # Lưu thông tin chia sẻ
        shared_url = SharedUrl(note_id=note_id, username=username, shared_at=datetime.utcnow())
        db.session.add(shared_url)
        db.session.commit()

        return jsonify({"message": "Note shared successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route để truy cập ghi chú chia sẻ
@notes.route('/notes/access', methods=['GET'])
@token_required
def access_shared_note():
    try:
        temp_url = request.args.get('temp_url')
        shared_note = SharedUrl.query.filter_by(temp_url=temp_url).first()
        if not shared_note:
            return jsonify({"error": "Shared note not found"}), 404

        # Lấy ghi chú đã chia sẻ
        note = Note.query.get(shared_note.note_id)
        if not note:
            return jsonify({"error": "Note not found"}), 404

        # Giải mã ghi chú
        decrypted_note = decrypt_note(note.content, shared_note.password, note.iv)

        return jsonify({"note": decrypted_note}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
