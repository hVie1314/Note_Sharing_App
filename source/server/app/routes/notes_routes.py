from flask import Blueprint, request
from app.controllers.note_controller import create_note, fetch_note, share_note, access_shared_note, fetch_user_notes, delete_note, get_shared_urls_by_user
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
    data = request.json
    return access_shared_note(data)


@note_bp.route('/notes/access/user_key', methods=['GET'])
@token_required
def get_sharing_key():
    data = request.json
    return access_shared_note(data)

@note_bp.route('/notes/list', methods=['GET'])
@token_required
def get_user_notes():
    return fetch_user_notes()

@note_bp.route('/notes/<int:note_id>', methods=['DELETE'])
@token_required
def delete_note_route(note_id):
    return delete_note(note_id)

@note_bp.route('/notes/shared/<username>', methods=['GET'])
@token_required
def get_shared_urls_route(username):
    return get_shared_urls_by_user(username)