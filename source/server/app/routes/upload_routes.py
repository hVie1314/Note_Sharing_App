from flask import Blueprint, request
from app.controllers.note_controller import upload_file
from app.utils.decorators import token_required

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
def upload_file_route():
    return upload_file()