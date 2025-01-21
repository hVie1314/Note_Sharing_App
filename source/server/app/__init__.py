from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    from app.routes.auth_routes import auth_bp
    from app.routes.upload_routes import upload_bp
    from app.routes.notes_routes import note_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(note_bp)
    
    return app
