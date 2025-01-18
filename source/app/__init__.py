from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    from app.controllers.auth_controller import auth
    from app.controllers.note_controller import notes
    
    app.register_blueprint(auth)
    app.register_blueprint(notes)
    
    return app
