from flask import Blueprint, request
from app.controllers.note_controller import create_note, fetch_note, share_note, access_shared_note, fetch_user_notes
from app.utils.decorators import token_required

note_bp = Blueprint('note', __name__)

@note_bp.route('/notes/create', methods=['POST'])
@token_required
def create_note_route():
    data = request.json
    return create_note(data)

@note_bp.route('/notes/<int:note_id>', methods=['GET'])
@token_required
def fetch_note_route(note_id):
    return fetch_note(note_id)

@note_bp.route('/notes/share', methods=['POST'])
@token_required
def share_note_route():
    data = request.json
    return share_note(data)

@note_bp.route('/notes/access', methods=['GET'])
@token_required
def access_shared_note_route():
    return access_shared_note()

@note_bp.route('/notes/list', methods=['GET'])
@token_required
def get_user_notes():
    return fetch_user_notes()