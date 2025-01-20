from flask import Blueprint, request, jsonify
from app.models.models import Note, SharedUrl
from app.utils.decorators import token_required
from app import db
import os
from datetime import datetime, timedelta
import uuid
from werkzeug.utils import secure_filename
from config import Config

notes = Blueprint('notes', __name__)

@notes.route('/upload', methods=['POST'])
@token_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    # ...existing upload code...

@notes.route('/notes', methods=['POST'])
@token_required
def upload_note():
    data = request.json
    filename = f"{uuid.uuid4()}.txt"
    # ...existing note upload code...

@notes.route('/notes/share', methods=['POST'])
@token_required
def share_note():
    data = request.json
    # ...existing share code...

@notes.route('/notes/access', methods=['GET'])
@token_required
def access_note():
    temp_url = request.args.get('temp_url')
    # ...existing access code...
