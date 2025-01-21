import requests
from .encryption import encrypt_note, decrypt_note
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

BASE_URL = "http://127.0.0.1:5000"  # Địa chỉ API server

def register(username, password):
    response = requests.post(f"{BASE_URL}/auth/register", json={"username": username, "password": password})
    if response.status_code == 201:
        return {
            "success": True,
            "message": "Registration successful!"
        }
    else:
        try:
            error_message = response.json().get('error')
        except requests.exceptions.JSONDecodeError:
            error_message = response.text
        return {
            "success": False,
            "message": error_message
        }


def login(username, password):
    response = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password})
    if response.status_code == 200:
        auth_token = response.json().get("token")
        return {
            "success": True,
            "token": auth_token
        }
    else:
        try:
            error_message = response.json().get('error')
        except requests.exceptions.JSONDecodeError:
            error_message = response.text
        return {
            "success": False,
            "message": error_message
        }


def logout(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)

    if response.status_code == 200:
        return {
            "success": True,
            "message": "Logout successful!"
        }
    else:
        try:
            error_message = response.json().get('error')
        except requests.exceptions.JSONDecodeError:
            error_message = response.text
        return {
            "success": False,
            "message": error_message
        }
        

def upload_file(auth_token, username, file_path):
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            headers = {"Authorization": f"Bearer {auth_token}"}
            data = {'username': username}
            
            response = requests.post(
                f"{BASE_URL}/upload",
                headers=headers,
                files=files,
                data=data
            )
            
            if response.status_code == 201:
                return {
                    "success": True,
                    "message": "File uploaded successfully",
                    "file_path": response.json().get("file_path")
                }
            else:
                return {
                    "success": False,
                    "error": response.json().get("error", "Upload failed")
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    
# Hàm tạo ghi chú (mã hóa ghi chú trước khi gửi lên server)
def create_note(auth_token, note_content, password, expires_at=None):
    encrypted_note = encrypt_note(note_content, password)  # Mã hóa ghi chú
    encrypted_note["expires_at"] = expires_at
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.post(
        f"{BASE_URL}/notes/create",
        json=encrypted_note,
        headers=headers,
    )
    return response.json()

# Hàm lấy và giải mã ghi chú
def fetch_and_decrypt_note(auth_token, note_id, password):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(f"{BASE_URL}/notes/{note_id}", headers=headers)
    if response.status_code == 200:
        encrypted_note = response.json()
        decrypted_note = decrypt_note(encrypted_note, password)  # Giải mã ghi chú
        return {"success": True, "note": decrypted_note}
    else:
        return {"success": False, "message": response.text}

def get_users(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(f"{BASE_URL}/auth/users", headers=headers)
    
    if response.status_code == 200:
        return {
            "success": True,
            "users": response.json().get("users")
        }
    else:
        try:
            error_message = response.json().get('error')
        except requests.exceptions.JSONDecodeError:
            error_message = response.text
        return {
            "success": False,
            "message": error_message
        }

def get_user_notes(auth_token):
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    try:
        response = requests.get(
            f"{BASE_URL}/notes",
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "success": False,
                "error": response.json().get("error", "Unknown error")
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }
    
def delete_note(auth_token, note_id):
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    try:
        response = requests.delete(
            f"{BASE_URL}/notes/{note_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "message": "Note deleted successfully"
            }
        else:
            return {
                "success": False,
                "error": response.json().get("error", "Delete failed")
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# from flask import request, jsonify
# from app.models.models import Note, SharedUrl
# from app.utils.decorators import token_required
# from app import db
# import os
# from datetime import datetime, timedelta
# from werkzeug.utils import secure_filename
# from config import Config


# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400
#     if file:
#         try:
#             filename = secure_filename(file.filename)
#             file_path = os.path.join(Config.UPLOAD_FOLDER, filename)

#             # Check if file already exists and rename if necessary
#             base, extension = os.path.splitext(filename)
#             counter = 1
#             while os.path.exists(file_path):
#                 filename = f"{base}({counter}){extension}"
#                 file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
#                 counter += 1
            
#             # os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
#             file.save(file_path)
            
#             # Save file path to database
#             new_note = Note(
#                 filename=filename,
#                 encryption_key="tmp_key",  # Thay thế bằng khóa mã hóa thực tế nếu có
#                 expires_at=None,
#                 username = request.form.get('username'),
#                 file_path=file_path
#             )
#             db.session.add(new_note)
#             db.session.commit()
            
#             return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 201
        
#         except Exception as e:
#             return jsonify({"error": str(e)}), 500

# # @notes.route('/notes', methods=['POST'])
# # @token_required
# # def upload_note():
# #     data = request.json
# #     #filename = f"{uuid.uuid4()}.txt"
# #     # ...existing note upload code...

# # @notes.route('/notes/share', methods=['POST'])
# # @token_required
# # def share_note():
# #     data = request.json
# #     # ...existing share code...

# # @notes.route('/notes/access', methods=['GET'])
# # @token_required
# # def access_note():
# #     temp_url = request.args.get('temp_url')
# #     # ...existing access code...