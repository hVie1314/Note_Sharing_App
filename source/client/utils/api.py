import os
import requests
from .encryption import encrypt_file, decrypt_file

BASE_URL = "http://127.0.0.1:5000"  # Địa chỉ API server


# fetures related to authentication
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
        
def get_user_key(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(f"{BASE_URL}/auth/user_key", headers=headers)
    if response.status_code == 200:
        return {
            "success": True,
            "encryption_key": response.json().get("encryption_key")
        }
    else:
        return {
            "success": False,
            "error": response.json().get("error", "Failed to retrieve user encryption key")
        } 


# features related to encryption file
def upload_file(auth_token, username, file_path):
    try:
        # Lấy khóa mã hóa của người dùng từ server
        user_key_response = get_user_key(auth_token)
        if not user_key_response["success"]:
            return {
                "success": False,
                "error": user_key_response["error"]
            }
        user_key = bytes.fromhex(user_key_response["encryption_key"])

        encrypted_file_info = encrypt_file(file_path, user_key)
        encrypted_file_path = encrypted_file_info["file_path"]

        with open(encrypted_file_path, 'rb') as f:
            files = {'file': f}
            headers = {"Authorization": f"Bearer {auth_token}"}
            data = {'username': username}
            
            response = requests.post(
                f"{BASE_URL}/upload",
                headers=headers,
                files=files,
                data=data
            )
        
        # Delete the encrypted file after uploading
        os.remove(encrypted_file_path)
            
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
        
def download_and_decrypt_file(auth_token, file_id):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.get(f"{BASE_URL}/download/{file_id}", headers=headers)
    if response.status_code == 200:
        encrypted_file_path = response.json().get("file_path")

        # Lấy khóa mã hóa của người dùng từ server
        user_key_response = get_user_key(auth_token)
        if not user_key_response["success"]:
            return {
                "success": False,
                "error": user_key_response["error"]
            }
        user_key = bytes.fromhex(user_key_response["encryption_key"])

        decrypted_file_path = decrypt_file(encrypted_file_path, user_key)
        return {"success": True, "file_path": decrypted_file_path}
    else:
        return {"success": False, "message": response.text}


# features related to UI
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
    
def get_sharing_notes(auth_token, url):
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    try:
        response = requests.get(
            f"{BASE_URL}/notes/access",
            headers=headers,
            json={
                "url_id": url,
            }
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
    
def create_share_url(auth_token, note_id, days, hours, minutes):
    """Tạo URL chia sẻ cho note với thời hạn"""
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    try:
         # Lấy khóa mã hóa của người dùng từ server
        user_key_response = get_user_key(auth_token)
        if not user_key_response["success"]:
            return {
                "success": False,
                "error": user_key_response["error"]
            }
        user_key = bytes.fromhex(user_key_response["encryption_key"])
        response = requests.post(
            f"{BASE_URL}/notes/share",
            headers=headers,
            json={
                "note_id": note_id,
                "expires_days": days,  # Thêm số ngày hết hạn
                "expires_hours": hours,
                "expires_minutes": minutes,
                "user_key": user_key_response["encryption_key"],
            }
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
    
def get_shared_urls(auth_token, username):
    """Lấy danh sách URLs được chia sẻ cho user"""
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    try:
        response = requests.get(
            f"{BASE_URL}/notes/shared/{username}",
            headers=headers
        )
        
        if response.status_code == 200:
            return {
                "success": True,
                "shared_urls": response.json().get("shared_urls", [])
            }
        else:
            return {
                "success": False,
                "error": response.json().get("error", "Failed to get shared URLs")
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }