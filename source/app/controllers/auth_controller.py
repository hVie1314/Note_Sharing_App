from app import db
from flask import  jsonify
from app.models.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.token_utils import generate_token
    
def register_user(username, password):
    """Xử lý đăng ký người dùng"""
    # Kiểm tra nếu user đã tồn tại
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400
    print(username)
    # Mã hóa mật khẩu và tạo user
    hashed_password = generate_password_hash(password)
    user = User(username=username, password=hashed_password)
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


def login_user(username, password):
    """Xử lý đăng nhập người dùng"""
    # Tìm user trong database
    user = User.query.filter_by(username=username).first()
    
    # Kiểm tra thông tin đăng nhập
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Sinh token mới và lưu vào database
    token = generate_token(user.id)
    user.token = token
    
    try:
        db.session.commit()
        return jsonify({"token": token}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
