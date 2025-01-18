from flask import Blueprint, request, jsonify
from app.models.models import User
from app import db
import uuid

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"error": "User already exists"}), 400
    
    user = User(username=data['username'], password=data['password'])
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@auth.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(
        username=data['username'], 
        password=data['password']
    ).first()
    
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    user.token = str(uuid.uuid4())
    db.session.commit()
    return jsonify({"token": user.token}), 200
