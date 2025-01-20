import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.getenv('USER')}:{os.getenv('PASSWORD_DATABASE')}@{os.getenv('HOST')}:{os.getenv('PORT')}/{os.getenv('DATABASE')}"
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = './uploads'
    NOTES_DIR = './notes'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
