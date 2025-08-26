from flask import Blueprint, request
from flask_restful import Api, Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from app.services.auth_service import AuthService
from app.api.auth.serializers import LoginSchema, UserSchema
from app.utils.response_helpers import success_response, error_response, validation_error_response
from app.api.middleware.auth import token_required
from marshmallow import ValidationError
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
auth_api = Api(auth_bp)

class LoginResource(Resource):
    def post(self):
        """User login endpoint"""
        try:
            schema = LoginSchema()
            data = schema.load(request.get_json() or {})
            
            auth_service = AuthService()
            result = auth_service.authenticate(data['username'], data['password'])
            
            if result:
                # Create JWT token
                token = create_access_token(
                    identity={'user_id': result['user']['id'], 'username': result['user']['username']},
                    expires_delta=timedelta(hours=24)
                )
                
                return success_response({
                    'token': token,
                    'user': result['user']
                })
            else:
                return error_response(
                    message="Invalid username or password",
                    code="INVALID_CREDENTIALS",
                    status_code=401
                )
                
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return error_response(
                message="Login failed",
                code="LOGIN_ERROR",
                status_code=500
            )

class LogoutResource(Resource):
    @token_required
    def post(self, current_user):
        """User logout endpoint"""
        try:
            # In a more sophisticated setup, you might want to blacklist the token
            # For now, we'll just return success as the client should discard the token
            return success_response(message="Logged out successfully")
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return error_response("Logout failed", status_code=500)

class ProfileResource(Resource):
    @token_required
    def get(self, current_user):
        """Get current user profile"""
        try:
            schema = UserSchema()
            user_data = schema.dump(current_user)
            return success_response({'user': user_data})
        except Exception as e:
            logger.error(f"Profile fetch error: {str(e)}")
            return error_response("Failed to fetch profile", status_code=500)

class RefreshTokenResource(Resource):
    @token_required
    def post(self, current_user):
        """Refresh JWT token"""
        try:
            token = create_access_token(
                identity={'user_id': current_user.id, 'username': current_user.username},
                expires_delta=timedelta(hours=24)
            )
            return success_response({'token': token})
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return error_response("Failed to refresh token", status_code=500)

# Register resources
auth_api.add_resource(LoginResource, '/login')
auth_api.add_resource(LogoutResource, '/logout')
auth_api.add_resource(ProfileResource, '/profile')
auth_api.add_resource(RefreshTokenResource, '/refresh')