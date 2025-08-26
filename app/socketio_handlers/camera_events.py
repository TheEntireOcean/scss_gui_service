from flask_socketio import emit, join_room, leave_room
from app.models.camera import Camera
from app import db
import logging

logger = logging.getLogger(__name__)

def register_camera_handlers(socketio):
    """Register camera-specific SocketIO event handlers"""
    
    @socketio.on('start_camera_stream')
    def handle_start_camera_stream(data):
        """Handle request to start camera streaming"""
        try:
            camera_id = data.get('camera_id')
            if not camera_id:
                emit('error', {'message': 'Camera ID required'})
                return
            
            camera = Camera.query.get(camera_id)
            if not camera:
                emit('error', {'message': 'Camera not found'})
                return
            
            # Update camera status
            camera.status = 'starting'
            camera.is_active = True
            db.session.commit()
            
            # Notify all clients in the camera room
            room = f'camera_{camera_id}'
            socketio.emit('camera_status_changed', {
                'camera_id': camera_id,
                'status': 'starting',
                'is_active': True,
                'message': 'Camera stream starting...'
            }, room=room)
            
            # Simulate stream startup (in real implementation, this would trigger the actual camera service)
            import threading
            import time
            
            def simulate_stream_start():
                time.sleep(2)  # Simulate startup delay
                camera.status = 'active'
                db.session.commit()
                
                socketio.emit('stream_started', {
                    'camera_id': camera_id,
                    'status': 'active',
                    'stream_url': f'/stream/camera_{camera_id}',
                    'message': 'Camera stream active'
                }, room=room)
            
            thread = threading.Thread(target=simulate_stream_start)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logger.error(f"Error starting camera stream: {str(e)}")
            emit('error', {'message': 'Failed to start camera stream'})
    
    @socketio.on('stop_camera_stream')
    def handle_stop_camera_stream(data):
        """Handle request to stop camera streaming"""
        try:
            camera_id = data.get('camera_id')
            if not camera_id:
                emit('error', {'message': 'Camera ID required'})
                return
            
            camera = Camera.query.get(camera_id)
            if not camera:
                emit('error', {'message': 'Camera not found'})
                return
            
            # Update camera status
            camera.status = 'inactive'
            camera.is_active = False
            db.session.commit()
            
            # Notify all clients in the camera room
            room = f'camera_{camera_id}'
            socketio.emit('camera_status_changed', {
                'camera_id': camera_id,
                'status': 'inactive',
                'is_active': False,
                'message': 'Camera stream stopped'
            }, room=room)
            
            socketio.emit('stream_stopped', {
                'camera_id': camera_id,
                'status': 'inactive',
                'message': 'Camera stream stopped'
            }, room=room)
            
        except Exception as e:
            logger.error(f"Error stopping camera stream: {str(e)}")
            emit('error', {'message': 'Failed to stop camera stream'})