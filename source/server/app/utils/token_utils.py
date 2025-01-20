import jwt
import datetime
from config import Config

def generate_token(user_id):
    """Sinh JWT token cho user"""
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),  # Token hết hạn sau 24 giờ
    }
    token = jwt.encode(payload, Config.SECRET_KEY, algorithm="HS256")
    return token

def decode_token(token):
    """Giải mã token JWT"""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        return "Token has expired"  # Token hết hạn
    except jwt.InvalidTokenError:
        return "Invalid token"  # Token không hợp lệ
