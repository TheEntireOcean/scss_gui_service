from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import decode_token
import logging
import time

logger = logging.getLogger(__name__)

def register_handlers(socketio):
    """Register all SocketIO event handlers"""
    
    @socketio.on('connect')
    def handle_connect(auth):
        """Handle client connection with authentication"""
        try:
            if auth and 'token' in auth:
                # Verify JWT token
                token_data = decode_token(auth['token'])
                user_id = token_data['sub']['user_id']
                username = token_data['sub']['username']
                
                logger.info(f"User {username} connected successfully")
                emit('connection_status', {
                    'status': 'connected',
                    'message': f'Welcome {username}!'
                })
                return True
            else:
                logger.warning("Connection attempt without authentication")
                emit('connection_status', {
                    'status': 'error',
                    'message': 'Authentication required'
                })
                return False
                
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            emit('connection_status', {
                'status': 'error',
                'message': 'Invalid authentication token'
            })
            return False
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        logger.info("Client disconnected")
    
    @socketio.on('join_camera_room')
    def handle_join_camera_room(data):
        """Join a camera-specific room for updates"""
        try:
            camera_id = data.get('camera_id')
            if camera_id:
                room = f'camera_{camera_id}'
                join_room(room)
                logger.info(f"Client joined camera room: {room}")
                emit('room_joined', {
                    'camera_id': camera_id,
                    'room': room,
                    'status': 'success'
                })
            else:
                emit('error', {'message': 'Camera ID required'})
        except Exception as e:
            logger.error(f"Error joining camera room: {str(e)}")
            emit('error', {'message': 'Failed to join camera room'})
    
    @socketio.on('leave_camera_room')
    def handle_leave_camera_room(data):
        """Leave a camera-specific room"""
        try:
            camera_id = data.get('camera_id')
            if camera_id:
                room = f'camera_{camera_id}'
                leave_room(room)
                logger.info(f"Client left camera room: {room}")
                emit('room_left', {
                    'camera_id': camera_id,
                    'room': room,
                    'status': 'success'
                })
        except Exception as e:
            logger.error(f"Error leaving camera room: {str(e)}")
            emit('error', {'message': 'Failed to leave camera room'})
    
    @socketio.on('request_camera_status')
    def handle_request_camera_status(data):
        """Handle request for current camera status"""
        try:
            from app.models.camera import Camera
            camera_id = data.get('camera_id')
            
            if camera_id:
                camera = Camera.query.get(camera_id)
                if camera:
                    emit('camera_status_update', {
                        'camera_id': camera_id,
                        'status': camera.status,
                        'is_active': camera.is_active,
                        'fps': camera.fps,
                        'resolution': {
                            'width': camera.resolution_width,
                            'height': camera.resolution_height
                        }
                    })
                else:
                    emit('error', {'message': 'Camera not found'})
            else:
                # Return status for all cameras
                cameras = Camera.query.all()
                camera_statuses = []
                for camera in cameras:
                    camera_statuses.append({
                        'camera_id': camera.id,
                        'status': camera.status,
                        'is_active': camera.is_active,
                        'name': camera.name
                    })
                emit('all_cameras_status', {'cameras': camera_statuses})
                
        except Exception as e:
            logger.error(f"Error getting camera status: {str(e)}")
            emit('error', {'message': 'Failed to get camera status'})
    
    @socketio.on('request_system_status')
    def handle_request_system_status():
        """Handle request for system status"""
        try:
            # This would integrate with actual system monitoring
            # For now, return mock data
            system_status = {
                'services': [
                    {'name': 'gui-service', 'status': 'running', 'health': 'healthy'},
                    {'name': 'detection-service', 'status': 'running', 'health': 'healthy'},
                    {'name': 'recognition-service', 'status': 'running', 'health': 'healthy'},
                    {'name': 'database', 'status': 'running', 'health': 'healthy'},
                    {'name': 'kafka', 'status': 'running', 'health': 'healthy'}
                ],
                'performance': {
                    'cpu_usage': 25.5,
                    'memory_usage': 68.2,
                    'gpu_usage': 45.0,
                    'disk_usage': 23.1
                },
                'timestamp': int(time.time())
            }
            
            emit('system_status_update', system_status)
            
        except Exception as e:
            logger.error(f"Error getting system status: {str(e)}")
            emit('error', {'message': 'Failed to get system status'})