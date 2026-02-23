import pandas as pd
import numpy as np
from datetime import datetime
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

SECTORS = [
    'Technology', 'Healthcare', 'Finance', 'E-commerce', 'Education',
    'Real Estate', 'Food & Beverage', 'Transportation', 'Energy',
    'Entertainment', 'Agriculture', 'Manufacturing', 'Other'
]

STAGES = ['Pre-Seed', 'Seed', 'Series A', 'Series B', 'Series C', 'Growth']

LOCATIONS = [
    'North America', 'Europe', 'Asia', 'South America', 'Africa',
    'Oceania', 'Global'
]

def load_data():
    investors = pd.read_csv(os.path.join(DATA_DIR, 'investors.csv'))
    startups = pd.read_csv(os.path.join(DATA_DIR, 'startups.csv'))
    return investors, startups

def save_matches(matches_df):
    matches_df.to_csv(os.path.join(DATA_DIR, 'matches.csv'), index=False)

def sector_match_score(investor_sectors, startup_sector):
    if pd.isna(investor_sectors) or pd.isna(startup_sector):
        return 0.0
    
    investor_sector_list = [s.strip().lower() for s in str(investor_sectors).split(',')]
    startup_sector = str(startup_sector).lower().strip()
    
    if startup_sector in investor_sector_list:
        return 1.0
    return 0.0

def stage_match_score(investor_stage_pref, startup_stage):
    if pd.isna(investor_stage_pref) or pd.isna(startup_stage):
        return 0.5
    
    investor_stage = str(investor_stage_pref).lower().strip()
    startup_stage = str(startup_stage).lower().strip()
    
    if investor_stage == startup_stage:
        return 1.0
    
    stage_order = ['pre-seed', 'seed', 'series a', 'series b', 'series c', 'growth']
    
    try:
        inv_idx = stage_order.index(investor_stage)
        start_idx = stage_order.index(startup_stage)
        distance = abs(inv_idx - start_idx)
        return max(0, 1 - (distance * 0.25))
    except ValueError:
        return 0.5

def location_match_score(investor_locations, startup_location):
    if pd.isna(investor_locations) or pd.isna(startup_location):
        return 0.5
    
    investor_loc_list = [l.strip().lower() for l in str(investor_locations).split(',')]
    startup_loc = str(startup_location).lower().strip()
    
    if 'global' in investor_loc_list or startup_loc == 'global':
        return 1.0
    if startup_loc in investor_loc_list:
        return 1.0
    return 0.3

def funding_match_score(min_check, max_check, funding_needed):
    if pd.isna(min_check) or pd.isna(max_check) or pd.isna(funding_needed):
        return 0.5
    
    min_check = float(min_check)
    max_check = float(max_check)
    funding_needed = float(funding_needed)
    
    if funding_needed == 0:
        return 0.5
    
    if min_check <= funding_needed <= max_check:
        return 1.0
    
    if funding_needed < min_check:
        ratio = funding_needed / min_check
        return max(0, ratio)
    
    if funding_needed > max_check:
        ratio = max_check / funding_needed
        return max(0, ratio)
    
    return 0.5

def compute_single_match(investor, startup):
    sector_score = sector_match_score(investor.get('sectors', ''), startup.get('sector', ''))
    stage_score = stage_match_score(investor.get('stage_preference', ''), startup.get('stage', ''))
    location_score = location_match_score(investor.get('locations', ''), startup.get('location', ''))
    funding_score = funding_match_score(
        investor.get('min_check', 0),
        investor.get('max_check', 0),
        startup.get('funding_needed', 0)
    )
    
    weights = {
        'sector': 0.40,
        'stage': 0.25,
        'location': 0.15,
        'funding': 0.20
    }
    
    total_score = (
        weights['sector'] * sector_score +
        weights['stage'] * stage_score +
        weights['location'] * location_score +
        weights['funding'] * funding_score
    )
    
    return {
        'sector_match': round(sector_score, 3),
        'stage_match': round(stage_score, 3),
        'location_match': round(location_score, 3),
        'funding_match': round(funding_score, 3),
        'score': round(total_score, 3)
    }

def compute_all_matches():
    investors, startups = load_data()
    
    if len(investors) == 0 or len(startups) == 0:
        return pd.DataFrame()
    
    matches = []
    
    for _, investor in investors.iterrows():
        for _, startup in startups.iterrows():
            match_result = compute_single_match(investor.to_dict(), startup.to_dict())
            
            matches.append({
                'investor_id': investor['id'],
                'startup_id': startup['id'],
                'score': match_result['score'],
                'sector_match': match_result['sector_match'],
                'stage_match': match_result['stage_match'],
                'location_match': match_result['location_match'],
                'funding_match': match_result['funding_match'],
                'computed_at': datetime.now().isoformat()
            })
    
    matches_df = pd.DataFrame(matches)
    save_matches(matches_df)
    
    return matches_df

def get_investor_matches(investor_id, top_n=10):
    investors, startups = load_data()
    matches = pd.read_csv(os.path.join(DATA_DIR, 'matches.csv'))
    
    if len(matches) == 0:
        matches = compute_all_matches()
    
    investor_matches = matches[matches['investor_id'] == investor_id]
    investor_matches = investor_matches.sort_values('score', ascending=False).head(top_n)
    
    result = []
    for _, match in investor_matches.iterrows():
        startup = startups[startups['id'] == match['startup_id']]
        if len(startup) > 0:
            startup_dict = startup.iloc[0].to_dict()
            startup_dict.pop('password_hash', None)
            startup_dict['match_score'] = match['score']
            startup_dict['match_details'] = {
                'sector': match['sector_match'],
                'stage': match['stage_match'],
                'location': match['location_match'],
                'funding': match['funding_match']
            }
            result.append(startup_dict)
    
    return result

def get_startup_matches(startup_id, top_n=10):
    investors, startups = load_data()
    matches = pd.read_csv(os.path.join(DATA_DIR, 'matches.csv'))
    
    if len(matches) == 0:
        matches = compute_all_matches()
    
    startup_matches = matches[matches['startup_id'] == startup_id]
    startup_matches = startup_matches.sort_values('score', ascending=False).head(top_n)
    
    result = []
    for _, match in startup_matches.iterrows():
        investor = investors[investors['id'] == match['investor_id']]
        if len(investor) > 0:
            investor_dict = investor.iloc[0].to_dict()
            investor_dict.pop('password_hash', None)
            investor_dict['match_score'] = match['score']
            investor_dict['match_details'] = {
                'sector': match['sector_match'],
                'stage': match['stage_match'],
                'location': match['location_match'],
                'funding': match['funding_match']
            }
            result.append(investor_dict)
    
    return result
