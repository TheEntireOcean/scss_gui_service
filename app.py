from app import create_app, socketio
from app.services.kafka_bridge import KafkaWebSocketBridge
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_and_configure_app():
    """Create and configure the Flask app with SocketIO"""
    app = create_app()
    
    # Initialize Kafka bridge
    kafka_config = {
        'bootstrap_servers': [os.getenv('KAFKA_BROKERS', 'localhost:9092')],
        'auto_offset_reset': 'latest',
        'enable_auto_commit': True,
        'group_id': 'gui-service-bridge'
    }
    
    # Create Kafka bridge instance
    kafka_bridge = KafkaWebSocketBridge(socketio, kafka_config)
    
    # Store reference in app context for shutdown
    app.kafka_bridge = kafka_bridge
    
    return app, kafka_bridge

app, kafka_bridge = create_and_configure_app()

@app.before_first_request
def start_background_services():
    """Start background services after app startup"""
    logger.info("Starting background services...")
    kafka_bridge.start()

if __name__ == '__main__':
    try:
        logger.info("Starting GUI Service with SocketIO support...")
        socketio.run(app, 
                    host='0.0.0.0', 
                    port=5000, 
                    debug=True,
                    use_reloader=False)  # Disable reloader to prevent duplicate threads
    finally:
        # Cleanup on shutdown
        if hasattr(app, 'kafka_bridge'):
            app.kafka_bridge.stop()