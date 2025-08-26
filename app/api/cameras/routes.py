from flask import Blueprint, request
from flask_restful import Api, Resource
from app.models.camera import Camera
from app import db
from app.api.cameras.serializers import CameraSchema, CameraCreateSchema, CameraUpdateSchema, CameraSettingsSchema
from app.utils.response_helpers import success_response, error_response, validation_error_response, paginated_response
from app.api.middleware.auth import token_required, admin_required
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

cameras_bp = Blueprint('cameras', __name__, url_prefix='/api/cameras')
cameras_api = Api(cameras_bp)

class CamerasListResource(Resource):
    @token_required
    def get(self, current_user):
        """Get list of cameras with pagination and filtering"""
        try:
            # Get query parameters
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 20, type=int), 100)
            status = request.args.get('status')
            camera_type = request.args.get('type')
            search = request.args.get('search')
            
            # Build query
            query = Camera.query
            
            if status:
                query = query.filter(Camera.status == status)
            if camera_type:
                query = query.filter(Camera.camera_type == camera_type)
            if search:
                query = query.filter(Camera.name.ilike(f'%{search}%'))
            
            # Paginate
            cameras_paginated = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            # Serialize data
            schema = CameraSchema(many=True)
            cameras_data = schema.dump(cameras_paginated.items)
            
            return paginated_response(
                items={'cameras': cameras_data},
                page=page,
                per_page=per_page,
                total=cameras_paginated.total,
                endpoint='cameras.cameraslistresource'
            )
            
        except Exception as e:
            logger.error(f"Error fetching cameras: {str(e)}")
            return error_response("Failed to fetch cameras", status_code=500)
    
    @admin_required
    def post(self, current_user):
        """Create a new camera"""
        try:
            schema = CameraCreateSchema()
            data = schema.load(request.get_json() or {})
            
            # Create new camera
            camera = Camera(
                name=data['name'],
                source=data['source'],
                camera_type=data['camera_type']
            )
            
            db.session.add(camera)
            db.session.commit()
            
            # Return created camera
            response_schema = CameraSchema()
            camera_data = response_schema.dump(camera)
            
            return success_response(
                data={'camera': camera_data},
                message="Camera created successfully",
                status_code=201
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except IntegrityError:
            db.session.rollback()
            return error_response(
                message="Camera with this name or source already exists",
                code="DUPLICATE_CAMERA",
                status_code=409
            )
        except Exception as e:
            logger.error(f"Error creating camera: {str(e)}")
            db.session.rollback()
            return error_response("Failed to create camera", status_code=500)

class CameraResource(Resource):
    @token_required
    def get(self, current_user, camera_id):
        """Get camera details"""
        try:
            camera = Camera.query.get_or_404(camera_id)
            schema = CameraSchema()
            camera_data = schema.dump(camera)
            
            return success_response(data={'camera': camera_data})
            
        except Exception as e:
            logger.error(f"Error fetching camera {camera_id}: {str(e)}")
            return error_response("Failed to fetch camera", status_code=500)
    
    @admin_required
    def put(self, current_user, camera_id):
        """Update camera"""
        try:
            camera = Camera.query.get_or_404(camera_id)
            schema = CameraUpdateSchema()
            data = schema.load(request.get_json() or {})
            
            # Update camera fields
            for field, value in data.items():
                setattr(camera, field, value)
            
            db.session.commit()
            
            # Return updated camera
            response_schema = CameraSchema()
            camera_data = response_schema.dump(camera)
            
            return success_response(
                data={'camera': camera_data},
                message="Camera updated successfully"
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            logger.error(f"Error updating camera {camera_id}: {str(e)}")
            db.session.rollback()
            return error_response("Failed to update camera", status_code=500)
    
    @admin_required
    def delete(self, current_user, camera_id):
        """Delete camera"""
        try:
            camera = Camera.query.get_or_404(camera_id)
            db.session.delete(camera)
            db.session.commit()
            
            return success_response(message="Camera deleted successfully")
            
        except Exception as e:
            logger.error(f"Error deleting camera {camera_id}: {str(e)}")
            db.session.rollback()
            return error_response("Failed to delete camera", status_code=500)

class CameraControlResource(Resource):
    @admin_required
    def post(self, current_user, camera_id, action):
        """Control camera (start/stop)"""
        try:
            camera = Camera.query.get_or_404(camera_id)
            
            if action == 'start':
                camera.status = 'active'
                camera.is_active = True
                message = "Camera started successfully"
            elif action == 'stop':
                camera.status = 'inactive'
                camera.is_active = False
                message = "Camera stopped successfully"
            else:
                return error_response("Invalid action", status_code=400)
            
            db.session.commit()
            
            # Return updated camera
            schema = CameraSchema()
            camera_data = schema.dump(camera)
            
            return success_response(
                data={'camera': camera_data},
                message=message
            )
            
        except Exception as e:
            logger.error(f"Error controlling camera {camera_id}: {str(e)}")
            db.session.rollback()
            return error_response(f"Failed to {action} camera", status_code=500)

class CameraSettingsResource(Resource):
    @admin_required
    def put(self, current_user, camera_id):
        """Update camera settings"""
        try:
            camera = Camera.query.get_or_404(camera_id)
            schema = CameraSettingsSchema()
            data = schema.load(request.get_json() or {})
            
            # Update camera settings
            if 'resolution_width' in data:
                camera.resolution_width = data['resolution_width']
            if 'resolution_height' in data:
                camera.resolution_height = data['resolution_height']
            if 'fps' in data:
                camera.fps = data['fps']
            if 'settings' in data:
                camera.settings = data['settings']
            
            db.session.commit()
            
            # Return updated camera
            response_schema = CameraSchema()
            camera_data = response_schema.dump(camera)
            
            return success_response(
                data={'camera': camera_data},
                message="Camera settings updated successfully"
            )
            
        except ValidationError as e:
            return validation_error_response(e.messages)
        except Exception as e:
            logger.error(f"Error updating camera settings {camera_id}: {str(e)}")
            db.session.rollback()
            return error_response("Failed to update camera settings", status_code=500)

class CameraDiscoveryResource(Resource):
    @admin_required
    def get(self, current_user):
        """Discover cameras on the network"""
        try:
            # This would integrate with camera discovery service
            # For now, return mock data
            discovered_cameras = [
                {
                    'source': 'rtsp://192.168.1.102:554/stream',
                    'name': 'Discovered Camera 1',
                    'type': 'rtsp',
                    'capabilities': {
                        'resolutions': ['1920x1080', '1280x720'],
                        'fps_options': [30, 25, 15]
                    }
                }
            ]
            
            return success_response(data={'discovered_cameras': discovered_cameras})
            
        except Exception as e:
            logger.error(f"Error discovering cameras: {str(e)}")
            return error_response