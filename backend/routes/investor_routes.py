from flask import Blueprint, request, jsonify
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth import verify_token, get_user_by_id, update_investor, get_all_investors
from matching import get_investor_matches, compute_all_matches

investor_bp = Blueprint('investor', __name__)

def get_current_user():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None, 'No token provided'
    return verify_token(token)

@investor_bp.route('/profile', methods=['GET'])
def get_profile():
    payload, error = get_current_user()
    if error:
        return jsonify({'error': error}), 401
    
    if payload['user_type'] != 'investor':
        return jsonify({'error': 'Not an investor'}), 403
    
    user = get_user_by_id(payload['user_id'], 'investor')
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user}), 200

@investor_bp.route('/profile', methods=['PUT'])
def update_profile():
    payload, error = get_current_user()
    if error:
        return jsonify({'error': error}), 401
    
    if payload['user_type'] != 'investor':
        return jsonify({'error': 'Not an investor'}), 403
    
    data = request.get_json()
    user, error = update_investor(payload['user_id'], data)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({'message': 'Profile updated', 'user': user}), 200

@investor_bp.route('/matches', methods=['GET'])
def get_matches():
    payload, error = get_current_user()
    if error:
        return jsonify({'error': error}), 401
    
    if payload['user_type'] != 'investor':
        return jsonify({'error': 'Not an investor'}), 403
    
    top_n = request.args.get('top', 10, type=int)
    compute_all_matches()
    
    matches = get_investor_matches(payload['user_id'], top_n)
    
    return jsonify({'matches': matches, 'count': len(matches)}), 200

@investor_bp.route('/all', methods=['GET'])
def list_all():
    investors = get_all_investors()
    return jsonify({'investors': investors, 'count': len(investors)}), 200
