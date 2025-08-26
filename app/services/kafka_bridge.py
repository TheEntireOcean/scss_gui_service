import json
import logging
import threading
import time
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class KafkaWebSocketBridge:
    """Bridge service to consume Kafka messages and forward to WebSocket clients"""
    
    def __init__(self, socketio, kafka_config: Optional[Dict[str, Any]] = None):
        self.socketio = socketio
        self.consumer = None
        self.running = False
        self.thread = None
        
        # Default Kafka configuration
        self.kafka_config = kafka_config or {
            'bootstrap_servers': ['localhost:9092'],
            'auto_offset_reset': 'latest',
            'enable_auto_commit': True,
            'group_id': 'gui-service-bridge',
            'value_deserializer': lambda m: json.loads(m.decode('utf-8')) if m else None
        }
        
        # Topic patterns to subscribe to
        self.topics = [
            'detections',
            'recognitions', 
            'tracks',
            'system-alerts',
            'camera-events'
        ]
    
    def start(self):
        """Start the Kafka consumer in a separate thread"""
        if self.running:
            logger.warning("Kafka bridge already running")
            return
        
        try:
            self.consumer = KafkaConsumer(*self.topics, **self.kafka_config)
            self.running = True
            
            self.thread = threading.Thread(target=self._consume_messages)
            self.thread.daemon = True
            self.thread.start()
            
            logger.info("Kafka bridge started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Kafka bridge: {str(e)}")
            self.running = False
    
    def stop(self):
        """Stop the Kafka consumer"""
        self.running = False
        
        if self.consumer:
            self.consumer.close()
        
        if self.thread:
            self.thread.join(timeout=5)
        
        logger.info("Kafka bridge stopped")
    
    def _consume_messages(self):
        """Main message consumption loop"""
        logger.info("Starting Kafka message consumption loop")
        
        while self.running:
            try:
                # Poll for messages with timeout
                message_batch = self.consumer.poll(timeout_ms=1000)
                
                for topic_partition, messages in message_batch.items():
                    topic = topic_partition.topic
                    
                    for message in messages:
                        try:
                            self._process_message(topic, message.value)
                        except Exception as e:
                            logger.error(f"Error processing message from {topic}: {str(e)}")
                
            except KafkaError as e:
                logger.error(f"Kafka error: {str(e)}")
                time.sleep(5)  # Wait before retrying
                
            except Exception as e:
                logger.error(f"Unexpected error in Kafka consumer: {str(e)}")
                time.sleep(1)
    
    def _process_message(self, topic: str, message_data: Dict[str, Any]):
        """Process a Kafka message and forward to appropriate WebSocket room"""
        if not message_data:
            return
        
        try:
            camera_id = message_data.get('camera_id')
            if not camera_id:
                logger.warning(f"Message from {topic} missing camera_id")
                return
            
            room = f'camera_{camera_id}'
            
            if topic == 'detections':
                self._handle_detection_message(room, camera_id, message_data)
                
            elif topic == 'recognitions':
                self._handle_recognition_message(room, camera_id, message_data)
                
            elif topic == 'tracks':
                self._handle_tracking_message(room, camera_id, message_data)
                
            elif topic == 'system-alerts':
                self._handle_system_alert(message_data)
                
            elif topic == 'camera-events':
                self._handle_camera_event(room, camera_id, message_data)
                
        except Exception as e:
            logger.error(f"Error processing {topic} message: {str(e)}")
    
    def _handle_detection_message(self, room: str, camera_id: str, data: Dict[str, Any]):
        """Handle detection message"""
        detections = data.get('detections', [])
        
        # Transform detection format if needed
        formatted_detections = []
        for detection in detections:
            formatted_detections.append({
                'bbox': detection.get('bbox', {}),
                'confidence': detection.get('confidence', 0.0),
                'class_name': detection.get('class_name', 'unknown'),
                'track_id': detection.get('track_id')
            })
        
        self.socketio.emit('detection_update', {
            'camera_id': camera_id,
            'timestamp': data.get('timestamp', int(time.time())),
            'detections': formatted_detections,
            'count': len(formatted_detections)
        }, room=room)
        
        logger.debug(f"Emitted {len(formatted_detections)} detections to {room}")
    
    def _handle_recognition_message(self, room: str, camera_id: str, data: Dict[str, Any]):
        """Handle recognition message"""
        recognitions = data.get('recognitions', [])
        
        # Transform recognition format if needed
        formatted_recognitions = []
        for recognition in recognitions:
            formatted_recognitions.append({
                'person_id': recognition.get('person_id'),
                'name': recognition.get('name', 'Unknown'),
                'confidence': recognition.get('confidence', 0.0),
                'bbox': recognition.get('bbox', {}),
                'track_id': recognition.get('track_id')
            })
        
        self.socketio.emit('recognition_update', {
            'camera_id': camera_id,
            'timestamp': data.get('timestamp', int(time.time())),
            'recognitions': formatted_recognitions,
            'count': len(formatted_recognitions)
        }, room=room)
        
        logger.debug(f"Emitted {len(formatted_recognitions)} recognitions to {room}")
    
    def _handle_tracking_message(self, room: str, camera_id: str, data: Dict[str, Any]):
        """Handle tracking message"""
        tracks = data.get('tracks', [])
        
        # Transform tracking format if needed
        formatted_tracks = []
        for track in tracks:
            formatted_tracks.append({
                'track_id': track.get('track_id'),
                'bbox': track.get('bbox', {}),
                'confidence': track.get('confidence', 0.0),
                'person_id': track.get('person_id'),
                'trajectory': track.get('trajectory', [])
            })
        
        self.socketio.emit('tracking_update', {
            'camera_id': camera_id,
            'timestamp': data.get('timestamp', int(time.time())),
            'tracks': formatted_tracks,
            'count': len(formatted_tracks)
        }, room=room)
        
        logger.debug(f"Emitted {len(formatted_tracks)} tracks to {room}")
    
    def _handle_system_alert(self, data: Dict[str, Any]):
        """Handle system-wide alerts"""
        self.socketio.emit('system_alert', {
            'type': data.get('type', 'info'),
            'message': data.get('message', ''),
            'timestamp': data.get('timestamp', int(time.time())),
            'severity': data.get('severity', 'low')
        })
        
        logger.info(f"Emitted system alert: {data.get('message', 'No message')}")
    
    def _handle_camera_event(self, room: str, camera_id: str, data: Dict[str, Any]):
        """Handle camera-specific events"""
        event_type = data.get('event_type', 'unknown')
        
        self.socketio.emit('camera_event', {
            'camera_id': camera_id,
            'event_type': event_type,
            'data': data.get('data', {}),
            'timestamp': data.get('timestamp', int(time.time()))
        }, room=room)
        
        logger.debug(f"Emitted camera event {event_type} to {room}")