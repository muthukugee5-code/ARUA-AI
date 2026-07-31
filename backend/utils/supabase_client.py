"""
ARUA AI - Supabase Client Utility
Centralized Supabase connection and helper functions
"""

import os
import logging
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', '')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', '')


def get_headers(use_service_key=False):
    """Get Supabase request headers."""
    key = SUPABASE_SERVICE_KEY if use_service_key else SUPABASE_ANON_KEY
    return {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }


def supabase_query(table, method='GET', data=None, filters=None, use_service_key=False):
    """Generic Supabase REST API query."""
    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL not configured")
    
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    
    if filters:
        query_params = []
        for key, value in filters.items():
            query_params.append(f"{key}=eq.{value}")
        url += '?' + '&'.join(query_params)
    
    headers = get_headers(use_service_key)
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, json=data, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        
        if response.text:
            return response.json()
        return []
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Supabase query error on {table}: {e}")
        raise


def supabase_auth_signup(email, password, user_metadata=None):
    """Sign up a new user with Supabase Auth (Admin API, auto-confirms)."""
    url = f"{SUPABASE_URL}/auth/v1/admin/users"
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'email': email,
        'password': password,
        'email_confirm': True
    }
    if user_metadata:
        payload['user_metadata'] = user_metadata
    
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    return response.json(), response.status_code


def supabase_auth_login(email, password):
    """Login a user with Supabase Auth."""
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Content-Type': 'application/json'
    }
    payload = {
        'email': email,
        'password': password
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    return response.json(), response.status_code


def supabase_verify_token(token):
    """Verify a JWT token with Supabase Auth."""
    url = f"{SUPABASE_URL}/auth/v1/user"
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        return response.json()
    return None


def upload_to_storage(bucket, file_path, file_content, content_type='image/png'):
    """Upload a file to Supabase Storage."""
    url = f"{SUPABASE_URL}/storage/v1/object/{bucket}/{file_path}"
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': content_type
    }
    
    response = requests.post(url, headers=headers, data=file_content, timeout=30)
    if response.status_code in [200, 201]:
        return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{file_path}"
    
    logger.error(f"Storage upload failed: {response.text}")
    return None


def get_public_url(bucket, file_path):
    """Get the public URL for a stored file."""
    return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{file_path}"
