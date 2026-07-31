"""
ARUA AI - Authentication API
User signup, login, logout, and password management
"""

import re
import logging
from flask import Blueprint, request, jsonify, g
from utils.supabase_client import (
    supabase_auth_signup, supabase_auth_login,
    supabase_query
)
from utils.auth_middleware import require_auth, rate_limit
from utils.credits import check_and_refill_credits
from datetime import datetime

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Valid"


@auth_bp.route('/signup', methods=['POST'])
@rate_limit(max_requests=5, window=300)
def signup():
    """Register a new user account."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request', 'message': 'JSON body required'}), 400
    
    # Extract and validate fields
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    
    # Validation
    if not username or len(username) < 3:
        return jsonify({'error': 'Validation error', 'message': 'Username must be at least 3 characters'}), 400
    
    if not validate_email(email):
        return jsonify({'error': 'Validation error', 'message': 'Invalid email address'}), 400
    
    if password != confirm_password:
        return jsonify({'error': 'Validation error', 'message': 'Passwords do not match'}), 400
    
    is_valid, msg = validate_password(password)
    if not is_valid:
        return jsonify({'error': 'Validation error', 'message': msg}), 400
    
    # Sanitize username
    if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
        return jsonify({'error': 'Validation error', 'message': 'Username can only contain letters, numbers, underscores, dots, and hyphens'}), 400
    
    try:
        # Create user with Supabase Auth
        auth_response, status_code = supabase_auth_signup(
            email, password,
            user_metadata={'username': username}
        )
        
        if status_code not in [200, 201]:
            error_msg = auth_response.get('msg', auth_response.get('message', 'Registration failed'))
            if 'already registered' in str(error_msg).lower():
                return jsonify({'error': 'Registration failed', 'message': 'Email already registered'}), 409
            return jsonify({'error': 'Registration failed', 'message': error_msg}), status_code
        
        user_id = auth_response.get('user', {}).get('id') or auth_response.get('id')
        
        # Create user profile in profiles table
        if user_id:
            try:
                supabase_query('profiles', method='POST', data={
                    'user_id': user_id,
                    'username': username,
                    'email': email,
                    'role': 'user',
                    'avatar_url': None,
                    'bio': '',
                    'ai_credits': 100,  # Free starting credits
                    'total_generated': 0,
                    'storage_used': 0,
                    'created_at': datetime.utcnow().isoformat()
                }, use_service_key=True)
            except Exception as profile_error:
                logger.warning(f"Profile creation failed for {user_id}: {profile_error}")
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully. Please check your email to confirm.',
            'user': {
                'id': user_id,
                'email': email,
                'username': username
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return jsonify({'error': 'Server error', 'message': 'Registration failed'}), 500


@auth_bp.route('/login', methods=['POST'])
@rate_limit(max_requests=10, window=300)
def login():
    """Authenticate user and return JWT tokens."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Invalid request', 'message': 'JSON body required'}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Validation error', 'message': 'Email and password required'}), 400
    
    if not validate_email(email):
        return jsonify({'error': 'Validation error', 'message': 'Invalid email format'}), 400
    
    try:
        auth_response, status_code = supabase_auth_login(email, password)
        
        if status_code != 200:
            error_msg = auth_response.get('error_description', auth_response.get('msg', 'Invalid credentials'))
            return jsonify({'error': 'Authentication failed', 'message': error_msg}), 401
        
        access_token = auth_response.get('access_token')
        refresh_token = auth_response.get('refresh_token')
        user_data = auth_response.get('user', {})
        user_id = user_data.get('id')
        
        # Auto-refill credits if 24h passed
        if user_id:
            check_and_refill_credits(user_id)

        # Fetch user profile
        profile = None
        if user_id:
            try:
                profiles = supabase_query('profiles', filters={'user_id': user_id}, use_service_key=True)
                profile = profiles[0] if profiles else None
                
                # Update last login
                if profile:
                    supabase_query(
                        f"profiles?user_id=eq.{user_id}",
                        method='PATCH',
                        data={'last_login': datetime.utcnow().isoformat()},
                        use_service_key=True
                    )
            except Exception as e:
                logger.warning(f"Profile fetch failed: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user_id,
                'email': user_data.get('email'),
                'username': profile.get('username') if profile else user_data.get('user_metadata', {}).get('username'),
                'avatar_url': profile.get('avatar_url') if profile else None,
                'ai_credits': profile.get('ai_credits', 100) if profile else 100,
                'role': profile.get('role', 'user') if profile else 'user'
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Server error', 'message': 'Login failed'}), 500


@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """Logout user (token invalidation handled client-side)."""
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200


@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_me():
    """Get current authenticated user's data."""
    try:
        user_id = g.user_id
        profiles = supabase_query('profiles', filters={'user_id': user_id}, use_service_key=True)
        profile = profiles[0] if profiles else {}
        
        return jsonify({
            'success': True,
            'user': {
                'id': user_id,
                'email': g.user.get('email'),
                'username': profile.get('username'),
                'avatar_url': profile.get('avatar_url'),
                'bio': profile.get('bio', ''),
                'ai_credits': profile.get('ai_credits', 0),
                'total_generated': profile.get('total_generated', 0),
                'storage_used': profile.get('storage_used', 0),
                'role': profile.get('role', 'user'),
                'created_at': profile.get('created_at')
            }
        }), 200
    except Exception as e:
        logger.error(f"Get user error: {e}")
        return jsonify({'error': 'Server error'}), 500
