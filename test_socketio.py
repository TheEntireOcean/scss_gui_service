import socketio
import time
import json

# Create SocketIO client
sio = socketio.SimpleClient()

try:
    # Connect with authentication (you'll need a valid JWT token)
    sio.connect('http://localhost:5000', auth={'token': 'your-jwt-token'})
    
    # Join a camera room
    sio.emit('join_camera_room', {'camera_id': '1'})
    
    # Listen for events
    while True:
        event = sio.receive(timeout=10)
        if event:
            print(f"Received: {event}")
        
except KeyboardInterrupt:
    print("Disconnecting...")
    sio.disconnect()