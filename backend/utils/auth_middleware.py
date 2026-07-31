"""
AURA AI - Authentication Middleware
JWT token verification and user authentication
"""

import os
import logging
from functools import wraps
from flask import request, jsonify, g
from utils.supabase_client import supabase_verify_token, supabase_query

logger = logging.getLogger(__name__)


def require_auth(f):
    """Decorator to require authentication on routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized', 'message': 'Missing or invalid token'}), 401
        
        token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Unauthorized', 'message': 'Token required'}), 401
        
        # Verify token with Supabase
        user = supabase_verify_token(token)
        
        if not user:
            return jsonify({'error': 'Unauthorized', 'message': 'Invalid or expired token'}), 401
        
        # Attach user to request context
        g.user = user
        g.user_id = user.get('id')
        g.token = token
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_admin(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized', 'message': 'Missing or invalid token'}), 401
        
        token = auth_header.split(' ')[1]
        user = supabase_verify_token(token)
        
        if not user:
            return jsonify({'error': 'Unauthorized', 'message': 'Invalid token'}), 401
        
        # Check admin role in profiles table
        try:
            profiles = supabase_query('profiles', filters={'user_id': user['id']}, use_service_key=True)
            if not profiles or profiles[0].get('role') != 'admin':
                return jsonify({'error': 'Forbidden', 'message': 'Admin access required'}), 403
        except Exception as e:
            logger.error(f"Admin check failed: {e}")
            return jsonify({'error': 'Server error'}), 500
        
        g.user = user
        g.user_id = user.get('id')
        g.token = token
        
        return f(*args, **kwargs)
    
    return decorated_function


def rate_limit(max_requests=60, window=60):
    """Simple in-memory rate limiting decorator."""
    from collections import defaultdict
    import time
    
    request_counts = defaultdict(list)
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use IP as rate limit key
            client_ip = request.remote_addr or 'unknown'
            now = time.time()
            
            # Clean old requests outside the window
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip]
                if now - req_time < window
            ]
            
            if len(request_counts[client_ip]) >= max_requests:
                return jsonify({
                    'error': 'Rate limited',
                    'message': f'Maximum {max_requests} requests per {window} seconds'
                }), 429
            
            request_counts[client_ip].append(now)
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
