from functools import wraps
from flask import request, jsonify
from app.models.models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token is missing!"}), 401
        user = User.query.filter_by(token=token).first()
        if not user:
            return jsonify({"error": "Invalid token!"}), 401
        return f(*args, **kwargs)
    return decorated