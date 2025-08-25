# gui-service/app/services/auth_service.py

from app.models.user import User
from app import db, bcrypt
from app.utils.jwt_helper import generate_jwt
from datetime import datetime

class AuthService:
    def authenticate(self, username: str, password: str):
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            token = generate_jwt(user.id, user.username, user.role)
            return {'token': token, 'user': user.to_dict()}
        return None

    def create_user(self, username: str, password: str, role: str = 'viewer'):
        if User.query.filter_by(username=username).first():
            return None
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password_hash=password_hash, role=role)
        db.session.add(user)
        db.session.commit()
        return user