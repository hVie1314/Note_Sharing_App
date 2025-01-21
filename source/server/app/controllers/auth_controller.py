from flask import jsonify
from app import db
from app.models.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.token_utils import generate_token

def register_user(username, password):
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400
        
    try:
        hashed_password = generate_password_hash(password)
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def login_user(username, password):
    try:
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({"error": "Invalid credentials"}), 401

        token = generate_token(user.id)
        user.token = token
        db.session.commit()
        return jsonify({"token": token}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def logout_user(token):
    try:
        user = User.query.filter_by(token=token).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        user.token = None
        db.session.commit()
        return jsonify({"message": "Logged out successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to log out", "details": str(e)}), 500
    
def get_all_users():
    try:
        users = User.query.all()
        users_list = [
            {
                'id': user.id,
                'username': user.username
            } for user in users
        ]
        return jsonify({'users': users_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500