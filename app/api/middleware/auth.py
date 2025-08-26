from functools import wraps
from flask import request, current_app
from flask_restful import abort
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from app.models.user import User
import jwt

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id['user_id'])
            if not current_user:
                abort(401, message="Invalid token")
            return f(current_user, *args, **kwargs)
        except Exception as e:
            abort(401, message="Token is invalid or expired")
    return decorated

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id['user_id'])
            if not current_user or current_user.role != 'admin':
                abort(403, message="Admin access required")
            return f(current_user, *args, **kwargs)
        except Exception as e:
            abort(401, message="Token is invalid or expired")
    return decorated

def optional_auth(f):
    """Decorator for optional authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
            current_user_id = get_jwt_identity()
            current_user = None
            if current_user_id:
                current_user = User.query.get(current_user_id['user_id'])
            return f(current_user, *args, **kwargs)
        except Exception:
            return f(None, *args, **kwargs)
    return decorated