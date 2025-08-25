# gui-service/app/utils/jwt_helper.py

from flask_jwt_extended import create_access_token, decode_token
from datetime import timedelta

def generate_jwt(user_id, username, role):
    return create_access_token(
        identity={'user_id': user_id, 'username': username, 'role': role},
        expires_delta=timedelta(hours=24)
    )

def verify_jwt(token):
    try:
        return decode_token(token)
    except:
        return None