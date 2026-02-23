from flask import Blueprint, request, jsonify
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth import create_investor, create_startup, authenticate_user, verify_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup/investor', methods=['POST'])
def signup_investor():
    data = request.get_json()
    
    required = ['email', 'password', 'name']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    investor, error = create_investor(data)
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({'message': 'Investor created', 'user': investor}), 201

@auth_bp.route('/signup/startup', methods=['POST'])
def signup_startup():
    data = request.get_json()
    
    required = ['email', 'password', 'name']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    startup, error = create_startup(data)
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({'message': 'Startup created', 'user': startup}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    required = ['email', 'password', 'user_type']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    if data['user_type'] not in ['investor', 'startup']:
        return jsonify({'error': 'user_type must be investor or startup'}), 400
    
    user, error = authenticate_user(data['email'], data['password'], data['user_type'])
    if error:
        return jsonify({'error': error}), 401
    
    return jsonify({'message': 'Login successful', 'user': user}), 200

@auth_bp.route('/verify', methods=['GET'])
def verify():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        return jsonify({'error': 'No token provided'}), 401
    
    payload, error = verify_token(token)
    if error:
        return jsonify({'error': error}), 401
    
    return jsonify({'valid': True, 'user': payload}), 200
