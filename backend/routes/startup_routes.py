from flask import Blueprint, request, jsonify
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth import verify_token, get_user_by_id, update_startup, get_all_startups
from matching import get_startup_matches, compute_all_matches

startup_bp = Blueprint('startup', __name__)

def get_current_user():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None, 'No token provided'
    return verify_token(token)

@startup_bp.route('/profile', methods=['GET'])
def get_profile():
    payload, error = get_current_user()
    if error:
        return jsonify({'error': error}), 401
    
    if payload['user_type'] != 'startup':
        return jsonify({'error': 'Not a startup'}), 403
    
    user = get_user_by_id(payload['user_id'], 'startup')
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user}), 200

@startup_bp.route('/profile', methods=['PUT'])
def update_profile():
    payload, error = get_current_user()
    if error:
        return jsonify({'error': error}), 401
    
    if payload['user_type'] != 'startup':
        return jsonify({'error': 'Not a startup'}), 403
    
    data = request.get_json()
    user, error = update_startup(payload['user_id'], data)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({'message': 'Profile updated', 'user': user}), 200

@startup_bp.route('/matches', methods=['GET'])
def get_matches():
    payload, error = get_current_user()
    if error:
        return jsonify({'error': error}), 401
    
    if payload['user_type'] != 'startup':
        return jsonify({'error': 'Not a startup'}), 403
    
    top_n = request.args.get('top', 10, type=int)
    compute_all_matches()
    
    matches = get_startup_matches(payload['user_id'], top_n)
    
    return jsonify({'matches': matches, 'count': len(matches)}), 200

@startup_bp.route('/all', methods=['GET'])
def list_all():
    startups = get_all_startups()
    return jsonify({'startups': startups, 'count': len(startups)}), 200
