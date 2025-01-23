from flask import Blueprint, request
from app.controllers.auth_controller import register_user, login_user, logout_user, get_user_key, get_all_users
from app.utils.decorators import token_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    return register_user(data['username'], data['password'])

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    return login_user(data['username'], data['password'])

@auth_bp.route('/auth/logout', methods=['POST'])
@token_required
def logout():
    token = request.headers.get('Authorization').split(" ")[1]
    return logout_user(token)

@auth_bp.route('/auth/user_key', methods=['GET'])
@token_required
def user_key_route():
    auth_token = request.headers.get('Authorization').split(" ")[1]
    return get_user_key(auth_token)

@auth_bp.route('/auth/users', methods=['GET'])
@token_required  
def get_users():
    return get_all_users()