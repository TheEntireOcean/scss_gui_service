# app/api/middleware/auth.py
from functools import wraps
from flask import request, current_app
from flask_restful import abort
from app.models.user import User
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                abort(401, message="Invalid token format")
        
        if not token:
            abort(401, message="Token is missing")
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first()
            if not current_user:
                abort(401, message="Invalid token")
        except jwt.ExpiredSignatureError:
            abort(401, message="Token has expired")
        except jwt.InvalidTokenError:
            abort(401, message="Invalid token")
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            abort(403, message="Admin access required")
        return f(current_user, *args, **kwargs)
    return decorated