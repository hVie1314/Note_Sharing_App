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
        

def upload_file(auth_token, username, file_path, password):
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    temp_path = None
    try:
        print(f"Starting upload for file: {file_path}")
        
        # Đọc và mã hóa file
        with open(file_path, 'rb') as f:
            content = f.read()
            encrypted_data = encrypt_note(content, password)
        
        # Tạo temporary file
        temp_filename = f"encrypted_{os.path.basename(file_path)}"
        temp_path = os.path.join(os.path.dirname(file_path), temp_filename)
        
        # Ghi file tạm và upload
        with open(temp_path, 'wb') as temp_file:
            temp_file.write(encrypted_data['ciphertext'])
        
        with open(temp_path, 'rb') as upload_file:
            files = {'file': (os.path.basename(file_path), upload_file)}
            data = {
                'username': username,
                'encryption_key': encrypted_data['key']
            }
            
            response = requests.post(
                f"{BASE_URL}/upload",
                headers=headers,
                files=files,
                data=data
            )
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                return {
                    "success": True,
                    "message": response_data.get("message", "File uploaded successfully"),
                    "file_path": response_data.get("file_path")
                }
            else:
                return {
                    "success": False,
                    "error": response.json().get("error", "Upload failed")
                }
            
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        # Cleanup temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception as e:
                print(f"Error removing temp file: {str(e)}")

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
            f"{BASE_URL}/notes/list",
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

def download_note(auth_token, note_id, save_path, password):
    """
    Download và giải mã file từ server.
    
    Args:
        auth_token (str): Token xác thực
        note_id (int): ID của note cần download
        save_path (str): Đường dẫn lưu file
        password (str): Mật khẩu để giải mã
        
    Returns:
        dict: Kết quả download với status và message
    """
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Download encrypted file
        response = requests.get(
            f"{BASE_URL}/notes/download/{note_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            # Lấy dữ liệu đã mã hóa
            encrypted_data = {
                "content": response.json()['content'],
                "iv": response.json()['iv']
            }
            
            # Giải mã
            decrypted_content = decrypt_note(encrypted_data, password)
            
            # Lưu file
            with open(save_path, 'wb') as f:
                f.write(decrypted_content.encode('utf-8'))
                
            return {
                "success": True,
                "message": "File downloaded successfully",
                "file_path": save_path
            }
        else:
            return {
                "success": False,
                "error": response.json().get("error", "Download failed")
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}
    
def create_share_url(auth_token, note_id):
    """Tạo URL chia sẻ cho note"""
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    try:
        response = requests.post(
            f"{BASE_URL}/notes/share",
            headers=headers,
            json={"note_id": note_id}
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "url": response.json().get("share_url")
            }
        else:
            return {
                "success": False,
                "error": response.json().get("error", "Failed to create share URL")
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }