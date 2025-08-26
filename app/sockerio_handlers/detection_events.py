from flask_socketio import emit
import logging
import time

logger = logging.getLogger(__name__)

def register_detection_handlers(socketio):
    """Register detection-specific SocketIO event handlers"""
    
    def emit_detection_update(camera_id, detections):
        """Emit detection update to camera room"""
        try:
            room = f'camera_{camera_id}'
            socketio.emit('detection_update', {
                'camera_id': camera_id,
                'timestamp': int(time.time()),
                'detections': detections,
                'count': len(detections) if detections else 0
            }, room=room)
            
        except Exception as e:
            logger.error(f"Error emitting detection update: {str(e)}")
    
    def emit_recognition_update(camera_id, recognitions):
        """Emit recognition update to camera room"""
        try:
            room = f'camera_{camera_id}'
            socketio.emit('recognition_update', {
                'camera_id': camera_id,
                'timestamp': int(time.time()),
                'recognitions': recognitions,
                'count': len(recognitions) if recognitions else 0
            }, room=room)
            
        except Exception as e:
            logger.error(f"Error emitting recognition update: {str(e)}")
    
    def emit_tracking_update(camera_id, tracks):
        """Emit tracking update to camera room"""
        try:
            room = f'camera_{camera_id}'
            socketio.emit('tracking_update', {
                'camera_id': camera_id,
                'timestamp': int(time.time()),
                'tracks': tracks,
                'count': len(tracks) if tracks else 0
            }, room=room)
            
        except Exception as e:
            logger.error(f"Error emitting tracking update: {str(e)}")
    
    # Store references for use by Kafka bridge
    socketio.emit_detection_update = emit_detection_update
    socketio.emit_recognition_update = emit_recognition_update
    socketio.emit_tracking_update = emit_tracking_update