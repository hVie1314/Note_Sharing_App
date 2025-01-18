from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import os
import uuid

app = Flask(__name__)

# Lưu trữ ghi chú
NOTES_DIR = './notes'
os.makedirs(NOTES_DIR, exist_ok=True)

# Mock database
users = {}
notes = {}
shared_urls = {}

# Đăng ký người dùng
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']  # Hash mật khẩu trong thực tế
    if username in users:
        return jsonify({"error": "User already exists"}), 400
    users[username] = {"password": password}
    return jsonify({"message": "User registered successfully"}), 201

# Đăng nhập
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    if username not in users or users[username]['password'] != password:
        return jsonify({"error": "Invalid credentials"}), 401
    token = str(uuid.uuid4())  # Mock token
    users[username]['token'] = token
    return jsonify({"token": token}), 200

# Upload ghi chú
@app.route('/notes', methods=['POST'])
def upload_note():
    data = request.json
    filename = f"{uuid.uuid4()}.txt"
    with open(os.path.join(NOTES_DIR, filename), 'w') as f:
        f.write(data['content'])  # Nội dung đã mã hóa
    note_id = len(notes) + 1
    notes[note_id] = {
        "filename": filename,
        "encryption_key": data['encryption_key'],
        "expires_at": data.get('expires_at')
    }
    return jsonify({"note_id": note_id}), 201

# Tạo URL tạm thời
@app.route('/notes/share', methods=['POST'])
def share_note():
    data = request.json
    note_id = data['note_id']
    if note_id not in notes:
        return jsonify({"error": "Note not found"}), 404
    temp_url = str(uuid.uuid4())
    shared_urls[temp_url] = {
        "note_id": note_id,
        "expires_at": datetime.utcnow() + timedelta(seconds=data['expires_in'])
    }
    return jsonify({"temp_url": temp_url}), 201

# Truy cập URL tạm thời
@app.route('/notes/access', methods=['GET'])
def access_note():
    temp_url = request.args.get('temp_url')
    if temp_url not in shared_urls or shared_urls[temp_url]['expires_at'] < datetime.utcnow():
        return jsonify({"error": "URL expired or invalid"}), 404
    note_id = shared_urls[temp_url]['note_id']
    note = notes[note_id]
    with open(os.path.join(NOTES_DIR, note['filename']), 'r') as f:
        content = f.read()
    return jsonify({"content": content, "encryption_key": note['encryption_key']}), 200

if __name__ == '__main__':
    app.run(debug=True)
