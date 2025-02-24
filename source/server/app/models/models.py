from app import db
import uuid
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), unique=True)
    encryption_key = db.Column(db.String(64), nullable=False) # key for encypt/decrpyt notes and share url

class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)  # Tên file
    file_path = db.Column(db.String(255), nullable=False)  # Đường dẫn lưu file
    username = db.Column(db.String(80), nullable=False)  # Người upload

class SharedUrl(db.Model):
    __tablename__ = 'shared_urls'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(64), unique=True, nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    username = db.Column(db.String(80), nullable=False)  # Thêm username
    note = db.relationship('Note')
    user_key = db.Column(db.String(64), nullable=False) 