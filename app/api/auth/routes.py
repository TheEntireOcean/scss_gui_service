# app/api/auth/routes.py
from flask import Blueprint
from flask_restful import Api, Resource, request
from app.services.auth_service import AuthService
from app.api.auth.serializers import LoginSchema, UserSchema
from app.utils.response_helpers import success_response, error_response
from app.api.middleware.auth import token_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
auth_api = Api(auth_bp)

class LoginResource(Resource):
    def post(self):
        schema = LoginSchema()
        try:
            data = schema.load(request.get_json() or {})
        except Exception as e:
            return error_response("Validation error", details=e.messages)
        
        auth_service = AuthService()
        result = auth_service.authenticate(data['username'], data['password'])
        
        if result:
            return success_response(result)
        return error_response("Invalid credentials", status_code=401)

class LogoutResource(Resource):
    @token_required
    def post(self, current_user):
        return success_response(message="Logged out successfully")

class ProfileResource(Resource):
    @token_required
    def get(self, current_user):
        schema = UserSchema()
        return success_response({
            'user': schema.dump(current_user)
        })

auth_api.add_resource(LoginResource, '/login')
auth_api.add_resource(LogoutResource, '/logout')
auth_api.add_resource(ProfileResource, '/profile')