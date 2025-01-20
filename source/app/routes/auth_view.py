from flask import Blueprint, request, jsonify
from app import db
from app.models.models import User
from app.utils.decorators import token_required
from app.controllers.auth_controller import register_user, login_user


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """Endpoint đăng ký người dùng"""
    data = request.json
    return register_user(data['username'], data['password'])


@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """Endpoint đăng nhập người dùng"""
    data = request.json
    return login_user(data['username'], data['password'])


@auth_bp.route('/auth//logout', methods=['POST'])
@token_required
def logout():
    token = request.headers.get('Authorization').split(" ")[1]
    user = User.query.filter_by(token=token).first()
    if user:
        try:
            # Xóa token của người dùng
            user.token = None
            db.session.commit()
            return jsonify({"message": "Logged out successfully"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Failed to log out", "details": str(e)}), 500
        
    return jsonify({"error": "User not found"}), 404