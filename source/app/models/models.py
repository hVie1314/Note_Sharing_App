from app import db

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
