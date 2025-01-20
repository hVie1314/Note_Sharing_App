import requests

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
    headers = {"Authorization": f"Bearer {auth_token}"}
    files = {'file': open(file_path, 'rb')}
    data = {'username': username}
    response = requests.post(f"{BASE_URL}/upload", headers=headers, files=files, data=data)
    if response.status_code == 201:
        return {
            "success": True,
            "message": "File uploaded successfully",
            "file_path": response.json().get("file_path")
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
