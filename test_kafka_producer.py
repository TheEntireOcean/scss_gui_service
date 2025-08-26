import json
import time
from kafka import KafkaProducer

# Create Kafka producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Send test detection message
detection_data = {
    'camera_id': '1',
    'timestamp': int(time.time()),
    'detections': [
        {
            'bbox': {'x': 100, 'y': 100, 'width': 50, 'height': 80},
            'confidence': 0.95,
            'class_name': 'person',
            'track_id': 'track_001'
        }
    ]
}

producer.send('detections', detection_data)
print("Sent test detection message")

producer.flush()
producer.close()