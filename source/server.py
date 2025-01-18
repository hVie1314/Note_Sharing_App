from functools import wraps
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import uuid
from sqlalchemy import text
from apscheduler.schedulers.background import BackgroundScheduler
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

app = Flask(__name__)

# SQLAlchemy configuration
# PostgreSQL configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('USER')}:{os.getenv('PASSWORD_DATABASE')}@{os.getenv('HOST')}:{os.getenv('PORT')}/{os.getenv('DATABASE')}"

# SQLite configuration (alternative)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define models
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    token = db.Column(db.String(36), unique=True)

class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    encryption_key = db.Column(db.String(100), nullable=False)
    expires_at = db.Column(db.DateTime)

class SharedUrl(db.Model):
    __tablename__ = 'shared_urls'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(36), unique=True, nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    note = db.relationship('Note')

# Lưu trữ ghi chú
NOTES_DIR = './notes'
os.makedirs(NOTES_DIR, exist_ok=True)

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

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
@token_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        safe_filename = f"{uuid.uuid4()}_{filename}"
        try:
            file.save(os.path.join(UPLOAD_FOLDER, safe_filename))
            return jsonify({
                "message": "File uploaded successfully",
                "filename": safe_filename
            }), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "File type not allowed"}), 400

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400
    
    user = User(username=username, password=password)
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    
    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    token = str(uuid.uuid4())
    user.token = token
    db.session.commit()
    return jsonify({"token": token}), 200

@app.route('/notes', methods=['POST'])
@token_required
def upload_note():
    data = request.json
    filename = f"{uuid.uuid4()}.txt"
    
    try:
        with open(os.path.join(NOTES_DIR, filename), 'w') as f:
            f.write(data['content'])
        
        note = Note(
            filename=filename,
            encryption_key=data['encryption_key'],
            expires_at=data.get('expires_at')
        )
        db.session.add(note)
        db.session.commit()
        return jsonify({"note_id": note.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/notes/share', methods=['POST'])
@token_required
def share_note():
    data = request.json
    note_id = data['note_id']
    temp_url = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(seconds=data['expires_in'])
    
    note = Note.query.get(note_id)
    if not note:
        return jsonify({"error": "Note not found"}), 404
    
    shared_url = SharedUrl(url=temp_url, note_id=note_id, expires_at=expires_at)
    try:
        db.session.add(shared_url)
        db.session.commit()
        return jsonify({"temp_url": temp_url}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/notes/access', methods=['GET'])
@token_required
def access_note():
    temp_url = request.args.get('temp_url')
    
    shared = SharedUrl.query.filter_by(url=temp_url).first()
    if not shared or shared.expires_at < datetime.utcnow():
        return jsonify({"error": "URL expired or invalid"}), 404
    
    try:
        with open(os.path.join(NOTES_DIR, shared.note.filename), 'r') as f:
            content = f.read()
        return jsonify({
            "content": content,
            "encryption_key": shared.note.encryption_key
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def cleanup_expired():
    with app.app_context():
        now = datetime.utcnow()
        # Cleanup expired notes
        expired_notes = Note.query.filter(Note.expires_at < now).all()
        for note in expired_notes:
            try:
                os.remove(os.path.join(NOTES_DIR, note.filename))
            except:
                pass
            db.session.delete(note)
        
        # Cleanup expired shared URLs
        expired_urls = SharedUrl.query.filter(SharedUrl.expires_at < now).all()
        for url in expired_urls:
            db.session.delete(url)
            
        db.session.commit()
        print(f"Cleanup completed at {now}")

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=cleanup_expired, trigger="interval", hours=1)

def test_db_connection():
    try:
        with app.app_context():
            # Sử dụng text() để wrap câu SQL
            db.session.execute(text('SELECT 1'))
            print('Kết nối database thành công!')
            # Tạo tables nếu chưa tồn tại
            db.create_all()
            print('Tạo tables thành công!')
    except Exception as e:
        print('Kết nối database thất bại!')
        print(f'Lỗi: {str(e)}')

if __name__ == '__main__':
    test_db_connection()
    scheduler.start()
    app.run(debug=True)
