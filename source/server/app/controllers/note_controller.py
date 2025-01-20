from flask import request, jsonify
from app.models.models import Note, SharedUrl
from app.utils.decorators import token_required
from app import db
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from config import Config


def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(Config.UPLOAD_FOLDER, filename)

            # Check if file already exists and rename if necessary
            base, extension = os.path.splitext(filename)
            counter = 1
            while os.path.exists(file_path):
                filename = f"{base}({counter}){extension}"
                file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                counter += 1
            
            # os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            file.save(file_path)
            
            # Save file path to database
            new_note = Note(
                filename=filename,
                encryption_key="tmp_key",  # Thay thế bằng khóa mã hóa thực tế nếu có
                expires_at=None,
                username = request.form.get('username'),
                file_path=file_path
            )
            db.session.add(new_note)
            db.session.commit()
            
            return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 201
        
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# @notes.route('/notes', methods=['POST'])
# @token_required
# def upload_note():
#     data = request.json
#     #filename = f"{uuid.uuid4()}.txt"
#     # ...existing note upload code...

# @notes.route('/notes/share', methods=['POST'])
# @token_required
# def share_note():
#     data = request.json
#     # ...existing share code...

# @notes.route('/notes/access', methods=['GET'])
# @token_required
# def access_note():
#     temp_url = request.args.get('temp_url')
#     # ...existing access code...
