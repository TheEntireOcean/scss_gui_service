# app/api/system/routes.py
from flask import Blueprint
from flask_restful import Api, Resource, request
from app.models.system_config import SystemConfig
from app import db
from app.api.system.serializers import SystemConfigSchema
from app.utils.response_helpers import success_response, error_response
from app.api.middleware.auth import token_required, admin_required
import time

system_bp = Blueprint('system', __name__, url_prefix='/api/system')
system_api = Api(system_bp)

class SystemConfigResource(Resource):
    @token_required
    def get(self, current_user):
        configs = SystemConfig.query.all()
        config_dict = {}
        
        for config in configs:
            config_dict[config.key] = config.value
        
        return success_response({
            'config': config_dict
        })
    
    @admin_required
    def put(self, current_user):
        data = request.get_json() or {}
        
        for key, value in data.items():
            config = SystemConfig.query.filter_by(key=key).first()
            if config:
                config.value = value
                config.updated_by = current_user.id
            else:
                config = SystemConfig(
                    key=key,
                    value=value,
                    category='general',
                    updated_by=current_user.id
                )
                db.session.add(config)
        
        db.session.commit()
        
        # Return updated config
        configs = SystemConfig.query.all()
        config_dict = {}
        for config in configs:
            config_dict[config.key] = config.value
        
        return success_response({
            'config': config_dict
        })

class SystemStatusResource(Resource):
    @token_required
    def get(self, current_user):
        # Mock system status - in real implementation, integrate with monitoring
        status = {
            'services': [
                {'name': 'gui-service', 'status': 'running', 'health': 'healthy'},
                {'name': 'detection-service', 'status': 'running', 'health': 'healthy'},
                {'name': 'recognition-service', 'status': 'running', 'health': 'healthy'},
                {'name': 'database', 'status': 'running', 'health': 'healthy'},
                {'name': 'kafka', 'status': 'running', 'health': 'healthy'}
            ],
            'performance': {
                'cpuUsage': 25.5,
                'memoryUsage': 68.2,
                'gpuUsage': 45.0,
                'diskUsage': 23.1
            },
            'timestamp': int(time.time())
        }
        
        return success_response(status)

class SystemResetResource(Resource):
    @admin_required
    def post(self, current_user):
        # Implement database reset logic here
        # WARNING: This is destructive!
        try:
            # Clear all tables except users and system_config
            from app.models.camera import Camera
            from app.models.person import Person
            
            db.session.query(Camera).delete()
            db.session.query(Person).delete()
            db.session.commit()
            
            return success_response(message="Database reset successfully")
        except Exception as e:
            db.session.rollback()
            return error_response("Failed to reset database", status_code=500)

system_api.add_resource(SystemConfigResource, '/config')
system_api.add_resource(SystemStatusResource, '/status')
system_api.add_resource(SystemResetResource, '/reset')