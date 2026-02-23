import os
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
SECRET_KEY = 'startupmatch_secret_key_2024'

os.makedirs(DATA_DIR, exist_ok=True)

def get_csv_path(filename):
    return os.path.join(DATA_DIR, filename)

def init_data_files():
    investors_path = get_csv_path('investors.csv')
    startups_path = get_csv_path('startups.csv')
    matches_path = get_csv_path('matches.csv')
    
    if not os.path.exists(investors_path):
        pd.DataFrame(columns=[
            'id', 'email', 'password_hash', 'name', 'company', 'sectors',
            'stage_preference', 'min_check', 'max_check', 'locations', 'created_at'
        ]).to_csv(investors_path, index=False)
    
    if not os.path.exists(startups_path):
        pd.DataFrame(columns=[
            'id', 'email', 'password_hash', 'name', 'description', 'sector',
            'stage', 'funding_needed', 'location', 'team_size', 'revenue',
            'growth_rate', 'created_at'
        ]).to_csv(startups_path, index=False)
    
    if not os.path.exists(matches_path):
        pd.DataFrame(columns=[
            'investor_id', 'startup_id', 'score', 'sector_match',
            'stage_match', 'location_match', 'funding_match', 'computed_at'
        ]).to_csv(matches_path, index=False)

def generate_id():
    import uuid
    return str(uuid.uuid4())[:8]

def create_investor(data):
    df = pd.read_csv(get_csv_path('investors.csv'))
    
    if len(df) > 0 and data['email'] in df['email'].values:
        return None, 'Email already exists'
    
    investor = {
        'id': generate_id(),
        'email': data['email'],
        'password_hash': generate_password_hash(data['password']),
        'name': data.get('name', ''),
        'company': data.get('company', ''),
        'sectors': ','.join(data.get('sectors', [])),
        'stage_preference': data.get('stage_preference', ''),
        'min_check': data.get('min_check', 0),
        'max_check': data.get('max_check', 0),
        'locations': ','.join(data.get('locations', [])),
        'created_at': datetime.now().isoformat()
    }
    
    df = pd.concat([df, pd.DataFrame([investor])], ignore_index=True)
    df.to_csv(get_csv_path('investors.csv'), index=False)
    
    investor.pop('password_hash')
    return investor, None

def create_startup(data):
    df = pd.read_csv(get_csv_path('startups.csv'))
    
    if len(df) > 0 and data['email'] in df['email'].values:
        return None, 'Email already exists'
    
    startup = {
        'id': generate_id(),
        'email': data['email'],
        'password_hash': generate_password_hash(data['password']),
        'name': data.get('name', ''),
        'description': data.get('description', ''),
        'sector': data.get('sector', ''),
        'stage': data.get('stage', ''),
        'funding_needed': data.get('funding_needed', 0),
        'location': data.get('location', ''),
        'team_size': data.get('team_size', 0),
        'revenue': data.get('revenue', 0),
        'growth_rate': data.get('growth_rate', 0),
        'created_at': datetime.now().isoformat()
    }
    
    df = pd.concat([df, pd.DataFrame([startup])], ignore_index=True)
    df.to_csv(get_csv_path('startups.csv'), index=False)
    
    startup.pop('password_hash')
    return startup, None

def authenticate_user(email, password, user_type):
    path = get_csv_path('investors.csv' if user_type == 'investor' else 'startups.csv')
    df = pd.read_csv(path)
    
    if len(df) == 0:
        return None, 'User not found'
    
    user = df[df['email'] == email]
    
    if len(user) == 0:
        return None, 'User not found'
    
    user = user.iloc[0]
    
    if not check_password_hash(user['password_hash'], password):
        return None, 'Invalid password'
    
    token = jwt.encode({
        'user_id': user['id'],
        'email': user['email'],
        'user_type': user_type,
        'exp': datetime.utcnow() + timedelta(days=7)
    }, SECRET_KEY, algorithm='HS256')
    
    user_dict = user.to_dict()
    user_dict.pop('password_hash')
    user_dict['token'] = token
    
    return user_dict, None

def get_user_by_id(user_id, user_type):
    path = get_csv_path('investors.csv' if user_type == 'investor' else 'startups.csv')
    df = pd.read_csv(path)
    
    user = df[df['id'] == user_id]
    if len(user) == 0:
        return None
    
    user_dict = user.iloc[0].to_dict()
    user_dict.pop('password_hash')
    return user_dict

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, 'Token expired'
    except jwt.InvalidTokenError:
        return None, 'Invalid token'

def get_all_investors():
    df = pd.read_csv(get_csv_path('investors.csv'))
    if len(df) == 0:
        return []
    df = df.drop(columns=['password_hash'])
    return df.to_dict('records')

def get_all_startups():
    df = pd.read_csv(get_csv_path('startups.csv'))
    if len(df) == 0:
        return []
    df = df.drop(columns=['password_hash'])
    return df.to_dict('records')

def update_investor(investor_id, data):
    df = pd.read_csv(get_csv_path('investors.csv'))
    idx = df[df['id'] == investor_id].index
    
    if len(idx) == 0:
        return None, 'Investor not found'
    
    idx = idx[0]
    
    for key, value in data.items():
        if key in df.columns and key not in ['id', 'email', 'password_hash']:
            if isinstance(value, list):
                df.at[idx, key] = ','.join(value)
            else:
                df.at[idx, key] = value
    
    df.to_csv(get_csv_path('investors.csv'), index=False)
    
    investor = df[df['id'] == investor_id].iloc[0].to_dict()
    investor.pop('password_hash')
    return investor, None

def update_startup(startup_id, data):
    df = pd.read_csv(get_csv_path('startups.csv'))
    idx = df[df['id'] == startup_id].index
    
    if len(idx) == 0:
        return None, 'Startup not found'
    
    idx = idx[0]
    
    for key, value in data.items():
        if key in df.columns and key not in ['id', 'email', 'password_hash']:
            df.at[idx, key] = value
    
    df.to_csv(get_csv_path('startups.csv'), index=False)
    
    startup = df[df['id'] == startup_id].iloc[0].to_dict()
    startup.pop('password_hash')
    return startup, None

init_data_files()
