# app/api/cameras/routes.py
from flask import Blueprint
from flask_restful import Api, Resource, request
from app.models.camera import Camera
from app import db
from app.api.cameras.serializers import CameraSchema, CameraCreateSchema, CameraUpdateSchema
from app.utils.response_helpers import success_response, error_response, paginated_response
from app.api.middleware.auth import token_required
from app.services.camera_discovery import CameraDiscoveryService
import math

cameras_bp = Blueprint('cameras', __name__, url_prefix='/api/cameras')
cameras_api = Api(cameras_bp)

class CameraListResource(Resource):
    @token_required
    def get(self, current_user):
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        status = request.args.get('status')
        
        query = Camera.query
        if status:
            query = query.filter_by(status=status)
        
        total = query.count()
        cameras = query.offset((page - 1) * per_page).limit(per_page).all()
        
        schema = CameraSchema(many=True)
        return paginated_response(
            items={'cameras': schema.dump(cameras)},
            page=page,
            per_page=per_page,
            total=total
        )
    
    @token_required
    def post(self, current_user):
        schema = CameraCreateSchema()
        try:
            data = schema.load(request.get_json() or {})
        except Exception as e:
            return error_response("Validation error", details=e.messages)
        
        camera = Camera(**data)
        db.session.add(camera)
        db.session.commit()
        
        result_schema = CameraSchema()
        return success_response({
            'camera': result_schema.dump(camera)
        }, status_code=201)

class CameraDetailResource(Resource):
    @token_required
    def get(self, current_user, camera_id):
        camera = Camera.query.get_or_404(camera_id)
        schema = CameraSchema()
        return success_response({
            'camera': schema.dump(camera)
        })
    
    @token_required
    def put(self, current_user, camera_id):
        camera = Camera.query.get_or_404(camera_id)
        schema = CameraUpdateSchema()
        
        try:
            data = schema.load(request.get_json() or {})
        except Exception as e:
            return error_response("Validation error", details=e.messages)
        
        for key, value in data.items():
            setattr(camera, key, value)
        
        db.session.commit()
        
        result_schema = CameraSchema()
        return success_response({
            'camera': result_schema.dump(camera)
        })
    
    @token_required
    def delete(self, current_user, camera_id):
        camera = Camera.query.get_or_404(camera_id)
        db.session.delete(camera)
        db.session.commit()
        return success_response(message="Camera deleted successfully")

class CameraStartResource(Resource):
    @token_required
    def post(self, current_user, camera_id):
        camera = Camera.query.get_or_404(camera_id)
        camera.status = 'active'
        camera.is_active = True
        db.session.commit()
        
        schema = CameraSchema()
        return success_response({
            'camera': schema.dump(camera)
        })

class CameraStopResource(Resource):
    @token_required
    def post(self, current_user, camera_id):
        camera = Camera.query.get_or_404(camera_id)
        camera.status = 'inactive'
        camera.is_active = False
        db.session.commit()
        
        schema = CameraSchema()
        return success_response({
            'camera': schema.dump(camera)
        })

class CameraSettingsResource(Resource):
    @token_required
    def put(self, current_user, camera_id):
        camera = Camera.query.get_or_404(camera_id)
        data = request.get_json() or {}
        
        if 'resolution_width' in data:
            camera.resolution_width = data['resolution_width']
        if 'resolution_height' in data:
            camera.resolution_height = data['resolution_height']
        if 'fps' in data:
            camera.fps = data['fps']
        if 'settings' in data:
            camera.settings = data['settings']
        
        db.session.commit()
        
        schema = CameraSchema()
        return success_response({
            'camera': schema.dump(camera)
        })

class CameraDiscoverResource(Resource):
    @token_required
    def get(self, current_user):
        discovery_service = CameraDiscoveryService()
        discovered = discovery_service.discover_rtsp_cameras("192.168.1.0/24")
        
        return success_response({
            'discovered_cameras': discovered
        })

cameras_api.add_resource(CameraListResource, '')
cameras_api.add_resource(CameraDetailResource, '/<int:camera_id>')
cameras_api.add_resource(CameraStartResource, '/<int:camera_id>/start')
cameras_api.add_resource(CameraStopResource, '/<int:camera_id>/stop')
cameras_api.add_resource(CameraSettingsResource, '/<int:camera_id>/settings')
cameras_api.add_resource(CameraDiscoverResource, '/discover')