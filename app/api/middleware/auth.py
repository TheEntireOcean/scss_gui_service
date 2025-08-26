# app/api/middleware/auth.py
from functools import wraps
from flask import request, current_app
from flask_restful import abort
from app.models.user import User
import jwt
import logging

logger = logging.getLogger(__name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                logger.error("Invalid token format")
                abort(401, message="Invalid token format")
        
        if not token:
            logger.error("Token is missing")
            abort(401, message="Token is missing")
        
        try:
            data = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            logger.debug(f"Decoded token data: {data}")
            user_id = data.get('sub', {}).get('user_id')
            if not user_id:
                logger.error("No user_id found in token payload")
                abort(401, message="Invalid token")
            current_user = User.query.filter_by(id=user_id).first()
            if not current_user:
                logger.error(f"No user found for user_id: {user_id}")
                abort(401, message="Invalid token")
            logger.debug(f"Current user: ID={current_user.id}, Username={current_user.username}, Role={current_user.role}")
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            abort(401, message="Token has expired")
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token error: {str(e)}")
            abort(401, message="Invalid token")
        
        return f(current_user=current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        current_user = kwargs.get('current_user')
        logger.debug(f"Admin check - User: {current_user.id if current_user else 'None'}, Role: {current_user.role if current_user else 'None'}, Role type: {type(current_user.role) if current_user else 'None'}")
        if not current_user or current_user.role.strip().lower() != 'admin':
            logger.error(f"User {current_user.id if current_user else 'unknown'} is not an admin. Role: {current_user.role if current_user else 'None'}")
            abort(403, message="Admin access required")
        return f(*args, **kwargs)
    return decorated