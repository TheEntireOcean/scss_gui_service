# GUI Service - Technical Architecture & Implementation Plan

**Version**: 1.0  
**Date**: August 24, 2025  
**Target**: Scalable Face Recognition System - GUI Component

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Backend Implementation Plan](#backend-implementation-plan)
4. [Frontend Implementation Plan](#frontend-implementation-plan)
5. [Database Schema](#database-schema)
6. [API Specifications](#api-specifications)
7. [Real-time Communication](#real-time-communication)
8. [Streaming Architecture](#streaming-architecture)
9. [Security Implementation](#security-implementation)
10. [Deployment Strategy](#deployment-strategy)
11. [Development Phases](#development-phases)
12. [Technology Stack](#technology-stack)

## Executive Summary

The GUI Service will be implemented as a full-stack application comprising:
- **Backend**: Flask application with GraphQL API, SocketIO, and direct PostgreSQL integration
- **Frontend**: React SPA with real-time streaming, overlays, and comprehensive camera management
- **Streaming**: Multi-tier streaming architecture (WebRTC → RTSP conversion → WebSocket fallback)
- **Authentication**: JWT-based simple login system
- **Real-time**: Kafka message forwarding service with WebSocket distribution

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GUI Service Architecture                  │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React)                                               │
│  ├── Camera Dashboard (Single + Thumbnails)                     │
│  ├── Real-time Overlays (Toggleable)                           │
│  ├── Configuration Management                                   │
│  └── Person Management (Onboarding)                            │
├─────────────────────────────────────────────────────────────────┤
│  Backend (Flask)                                                │
│  ├── GraphQL API (Authentication, CRUD)                        │
│  ├── SocketIO Server (Real-time updates)                       │
│  ├── Camera Discovery Service                                   │
│  └── Stream Management                                          │
├─────────────────────────────────────────────────────────────────┤
│  Supporting Services                                             │
│  ├── Kafka-WebSocket Bridge                                     │
│  ├── WebRTC Streaming Service                                   │
│  ├── RTSP-WebRTC Converter                                      │
│  └── Authentication Service                                     │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer                                                      │
│  ├── PostgreSQL (Direct Connection)                             │
│  ├── Redis (Session & Cache)                                    │
│  └── File Storage (Person Images)                               │
└─────────────────────────────────────────────────────────────────┘
```

## Backend Implementation Plan

### Core Flask Application Structure

```
gui-service/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── camera.py
│   │   ├── person.py
│   │   ├── user.py
│   │   └── system_config.py
│   ├── graphql/
│   │   ├── __init__.py
│   │   ├── schema.py
│   │   ├── queries/
│   │   │   ├── camera_queries.py
│   │   │   ├── person_queries.py
│   │   │   └── system_queries.py
│   │   └── mutations/
│   │       ├── camera_mutations.py
│   │       ├── person_mutations.py
│   │       └── auth_mutations.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── camera_discovery.py
│   │   ├── stream_manager.py
│   │   ├── kafka_bridge.py
│   │   └── onboarding_service.py
│   ├── socketio_handlers/
│   │   ├── __init__.py
│   │   ├── camera_events.py
│   │   ├── detection_events.py
│   │   └── system_events.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── jwt_helper.py
│   │   └── validators.py
│   └── config.py
├── streaming-services/
│   ├── webrtc-service/
│   │   ├── webrtc_server.py
│   │   └── signaling_server.py
│   ├── rtsp-converter/
│   │   ├── rtsp_to_webrtc.py
│   │   └── stream_proxy.py
│   └── kafka-bridge/
│       ├── kafka_consumer.py
│       └── websocket_forwarder.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

### Key Backend Components

#### 1. GraphQL Schema Design

```python
# Core GraphQL Types
type Camera {
    id: ID!
    name: String!
    source: String!
    type: CameraType!
    status: CameraStatus!
    resolution: Resolution
    fps: Int
    settings: CameraSettings
    isActive: Boolean!
    createdAt: DateTime!
    updatedAt: DateTime!
}

type Person {
    id: ID!
    name: String!
    images: [String!]!
    embeddings: [Embedding!]!
    createdAt: DateTime!
    lastSeen: DateTime
    confidence: Float
}

type SystemConfig {
    detectionThreshold: Float!
    recognitionConfidence: Float!
    samplingRate: Int!
    performanceMode: PerformanceMode!
}
```

#### 2. Authentication System

- JWT-based authentication
- Simple username/password login
- Session management with Redis
- Role-based permissions (Admin, Viewer)

#### 3. Camera Discovery Service

```python
class CameraDiscoveryService:
    def discover_rtsp_cameras(self, ip_range: str) -> List[Camera]
    def test_rtsp_connection(self, rtsp_url: str) -> bool
    def get_camera_capabilities(self, camera_id: str) -> CameraCapabilities
    def auto_configure_optimal_settings(self, camera_id: str) -> CameraSettings
```

## Frontend Implementation Plan

### React Application Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   ├── LoadingSpinner.jsx
│   │   │   └── ErrorBoundary.jsx
│   │   ├── camera/
│   │   │   ├── CameraDashboard.jsx
│   │   │   ├── CameraGrid.jsx
│   │   │   ├── CameraPlayer.jsx
│   │   │   ├── CameraControls.jsx
│   │   │   ├── CameraThumbnail.jsx
│   │   │   └── OverlayControls.jsx
│   │   ├── overlays/
│   │   │   ├── DetectionOverlay.jsx
│   │   │   ├── RecognitionOverlay.jsx
│   │   │   ├── TrackingOverlay.jsx
│   │   │   ├── PoseOverlay.jsx
│   │   │   └── DebugOverlay.jsx
│   │   ├── configuration/
│   │   │   ├── CameraSettings.jsx
│   │   │   ├── SystemSettings.jsx
│   │   │   ├── DetectionConfig.jsx
│   │   │   └── PerformanceConfig.jsx
│   │   ├── person-management/
│   │   │   ├── PersonList.jsx
│   │   │   ├── PersonCard.jsx
│   │   │   ├── OnboardingModal.jsx
│   │   │   ├── PhotoCapture.jsx
│   │   │   └── PersonDetails.jsx
│   │   └── system/
│   │       ├── SystemStatus.jsx
│   │       ├── ServiceHealth.jsx
│   │       ├── PerformanceMetrics.jsx
│   │       └── SystemControls.jsx
│   ├── hooks/
│   │   ├── useGraphQL.js
│   │   ├── useSocket.js
│   │   ├── useAuth.js
│   │   ├── useCamera.js
│   │   └── useRealtime.js
│   ├── services/
│   │   ├── graphql/
│   │   │   ├── client.js
│   │   │   ├── queries.js
│   │   │   └── mutations.js
│   │   ├── streaming/
│   │   │   ├── webrtc-client.js
│   │   │   ├── websocket-client.js
│   │   │   └── stream-manager.js
│   │   ├── auth.js
│   │   └── socket.js
│   ├── utils/
│   │   ├── constants.js
│   │   ├── helpers.js
│   │   └── validators.js
│   ├── styles/
│   │   ├── globals.css
│   │   ├── components/
│   │   └── themes/
│   ├── App.jsx
│   └── index.js
├── public/
├── package.json
└── webpack.config.js
```

### Key Frontend Features

#### 1. Dashboard Layout
- **Main View**: Single camera display (full screen)
- **Thumbnail Panel**: Grid of all active cameras (right sidebar)
- **Control Panel**: Camera controls and overlay toggles (bottom panel)
- **Status Bar**: System information and alerts (top)

#### 2. Toggleable Overlays
```javascript
const overlayTypes = {
  DETECTION_BOXES: 'detection_boxes',
  RECOGNITION_LABELS: 'recognition_labels',
  TRACKING_IDS: 'tracking_ids',
  POSE_ESTIMATION: 'pose_estimation',
  CONFIDENCE_SCORES: 'confidence_scores',
  FPS_DEBUG: 'fps_debug',
  SYSTEM_METRICS: 'system_metrics'
};
```

#### 3. Real-time Data Integration
- WebSocket connection for live metadata
- GraphQL subscriptions for configuration changes
- Event-driven overlay updates
- Buffered data management for smooth rendering

## Database Schema

### Extended PostgreSQL Schema

```sql
-- Users table for authentication
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'viewer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Cameras table
CREATE TABLE cameras (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    source VARCHAR(500) NOT NULL,
    camera_type VARCHAR(50) NOT NULL, -- 'rtsp', 'webcam', 'usb'
    status VARCHAR(50) DEFAULT 'inactive',
    resolution_width INTEGER DEFAULT 1920,
    resolution_height INTEGER DEFAULT 1080,
    fps INTEGER DEFAULT 30,
    settings JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System configuration
CREATE TABLE system_config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    category VARCHAR(100) NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(id)
);

-- Persons table (enhanced from original)
CREATE TABLE persons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    images TEXT[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP
);

-- Embeddings table (enhanced from original)
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    person_id INTEGER REFERENCES persons(id) ON DELETE CASCADE,
    embedding BYTEA NOT NULL,
    image_path VARCHAR(500),
    confidence FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tracks table for tracking data
CREATE TABLE tracks (
    id SERIAL PRIMARY KEY,
    camera_id INTEGER REFERENCES cameras(id),
    person_id INTEGER REFERENCES persons(id),
    track_id VARCHAR(255),
    bbox JSONB, -- {x, y, width, height}
    confidence FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Sessions table for authentication
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_cameras_status ON cameras(status);
CREATE INDEX idx_cameras_active ON cameras(is_active);
CREATE INDEX idx_persons_name ON persons(name);
CREATE INDEX idx_embeddings_person ON embeddings(person_id);
CREATE INDEX idx_tracks_camera ON tracks(camera_id);
CREATE INDEX idx_tracks_timestamp ON tracks(timestamp);
CREATE INDEX idx_sessions_token ON user_sessions(token_hash);
CREATE INDEX idx_sessions_user ON user_sessions(user_id);
```

## API Specifications

### GraphQL Queries

```graphql
# Camera Management
query GetCameras {
  cameras {
    id
    name
    source
    status
    resolution { width height }
    fps
    isActive
  }
}

query GetCameraDetails($id: ID!) {
  camera(id: $id) {
    id
    name
    source
    type
    status
    settings
    capabilities
  }
}

# Person Management
query GetPersons {
  persons {
    id
    name
    images
    lastSeen
    confidence
  }
}

# System Configuration
query GetSystemConfig {
  systemConfig {
    detectionThreshold
    recognitionConfidence
    samplingRate
    performanceMode
  }
}

# System Status
query GetSystemStatus {
  systemStatus {
    services {
      name
      status
      health
    }
    performance {
      cpuUsage
      memoryUsage
      gpuUsage
    }
  }
}
```

### GraphQL Mutations

```graphql
# Authentication
mutation Login($username: String!, $password: String!) {
  login(username: $username, password: $password) {
    token
    user {
      id
      username
      role
    }
  }
}

# Camera Management
mutation AddCamera($input: CameraInput!) {
  addCamera(input: $input) {
    id
    name
    source
    status
  }
}

mutation UpdateCameraSettings($id: ID!, $settings: CameraSettingsInput!) {
  updateCameraSettings(id: $id, settings: $settings) {
    id
    settings
  }
}

mutation StartCamera($id: ID!) {
  startCamera(id: $id) {
    id
    status
  }
}

mutation StopCamera($id: ID!) {
  stopCamera(id: $id) {
    id
    status
  }
}

# Person Management
mutation AddPerson($input: PersonInput!) {
  addPerson(input: $input) {
    id
    name
    images
  }
}

mutation UpdateSystemConfig($input: SystemConfigInput!) {
  updateSystemConfig(input: $input) {
    detectionThreshold
    recognitionConfidence
    samplingRate
  }
}

# System Controls
mutation ResetDatabase {
  resetDatabase {
    success
    message
  }
}
```

## Real-time Communication

### SocketIO Event Structure

```javascript
// Client to Server Events
const clientEvents = {
  // Camera Events
  JOIN_CAMERA_ROOM: 'join_camera_room',
  LEAVE_CAMERA_ROOM: 'leave_camera_room',
  REQUEST_CAMERA_STATUS: 'request_camera_status',
  
  // Configuration Events
  UPDATE_OVERLAY_SETTINGS: 'update_overlay_settings',
  REQUEST_SYSTEM_STATUS: 'request_system_status',
  
  // Control Events
  START_CAMERA_STREAM: 'start_camera_stream',
  STOP_CAMERA_STREAM: 'stop_camera_stream'
};

// Server to Client Events
const serverEvents = {
  // Detection Events
  DETECTION_UPDATE: 'detection_update',
  RECOGNITION_UPDATE: 'recognition_update',
  TRACKING_UPDATE: 'tracking_update',
  
  // System Events
  CAMERA_STATUS_CHANGED: 'camera_status_changed',
  SYSTEM_ALERT: 'system_alert',
  PERFORMANCE_METRICS: 'performance_metrics',
  
  // Stream Events
  STREAM_STARTED: 'stream_started',
  STREAM_STOPPED: 'stream_stopped',
  STREAM_ERROR: 'stream_error'
};
```

### Kafka-WebSocket Bridge Architecture

```python
class KafkaWebSocketBridge:
    def __init__(self):
        self.kafka_consumer = KafkaConsumer(
            'detections/*', 'recognitions/*', 'tracks/*',
            bootstrap_servers=['kafka:9092']
        )
        self.socketio = SocketIO()
    
    def consume_and_forward(self):
        for message in self.kafka_consumer:
            topic = message.topic
            camera_id = topic.split('/')[-1]
            
            if 'detections' in topic:
                self.socketio.emit('detection_update', {
                    'camera_id': camera_id,
                    'detections': message.value
                }, room=f'camera_{camera_id}')
            
            elif 'recognitions' in topic:
                self.socketio.emit('recognition_update', {
                    'camera_id': camera_id,
                    'recognitions': message.value
                }, room=f'camera_{camera_id}')
            
            elif 'tracks' in topic:
                self.socketio.emit('tracking_update', {
                    'camera_id': camera_id,
                    'tracks': message.value
                }, room=f'camera_{camera_id}')
```

## Streaming Architecture

### Multi-Tier Streaming Strategy

```
Priority 1: WebRTC Direct Streaming
├── Best quality and lowest latency
├── Direct peer-to-peer connection
└── Fallback on connection issues

Priority 2: RTSP to WebRTC Conversion
├── Server-side conversion service
├── Maintains quality with slight latency
└── Fallback for incompatible cameras

Priority 3: WebSocket Streaming (Fallback)
├── JPEG frame streaming over WebSocket
├── Higher latency but maximum compatibility
└── Automatic quality adjustment
```

### WebRTC Implementation

```javascript
class WebRTCStreamManager {
  constructor() {
    this.connections = new Map();
    this.signaling = new SignalingClient();
  }

  async startStream(cameraId) {
    const pc = new RTCPeerConnection({
      iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
    });
    
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    
    const answer = await this.signaling.sendOffer(cameraId, offer);
    await pc.setRemoteDescription(answer);
    
    this.connections.set(cameraId, pc);
    return pc;
  }

  stopStream(cameraId) {
    const connection = this.connections.get(cameraId);
    if (connection) {
      connection.close();
      this.connections.delete(cameraId);
    }
  }
}
```

## Security Implementation

### JWT Authentication Flow

```python
class AuthService:
    def authenticate(self, username: str, password: str) -> Optional[dict]:
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            token = jwt.encode({
                'user_id': user.id,
                'username': user.username,
                'role': user.role,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, current_app.config['SECRET_KEY'])
            return {'token': token, 'user': user.to_dict()}
        return None

    def verify_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
```

### Input Validation and Security

```python
# GraphQL input validation
class CameraInput:
    name: str = Field(min_length=1, max_length=255)
    source: str = Field(regex=r'^(rtsp://|http://|/dev/)')
    camera_type: str = Field(enum=['rtsp', 'webcam', 'usb'])
    
# SQL injection prevention
def get_person_by_id(person_id: int) -> Optional[Person]:
    return Person.query.filter(Person.id == person_id).first()
```

## Deployment Strategy

### Docker Configuration

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000 5001

CMD ["python", "app.py"]
```

```dockerfile
# Frontend Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gui-service-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: gui-service-backend
  template:
    spec:
      containers:
      - name: flask-app
        image: gui-service-backend:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: KAFKA_BROKERS
          value: "kafka:9092"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

## Development Phases

### Phase 1: Core Backend (Week 1-2)
1. **Setup Flask Application**
   - Project structure and configuration
   - Database models and migrations
   - Basic authentication system

2. **GraphQL API Implementation**
   - Schema definition
   - Query and mutation resolvers
   - Basic CRUD operations

3. **Database Integration**
   - PostgreSQL connection setup
   - Model definitions
   - Migration scripts

### Phase 2: Real-time Communication (Week 3)
1. **SocketIO Integration**
   - Event handlers setup
   - Room management for cameras
   - Basic message forwarding

2. **Kafka Bridge Service**
   - Kafka consumer setup
   - Message parsing and forwarding
   - Error handling and reconnection

### Phase 3: Frontend Foundation (Week 4-5)
1. **React Application Setup**
   - Project structure and routing
   - Component architecture
   - State management (Context API)

2. **Authentication UI**
   - Login/logout functionality
   - JWT token management
   - Protected routes

3. **Basic Dashboard**
   - Camera grid layout
   - Basic controls
   - Navigation structure

### Phase 4: Camera Management (Week 6-7)
1. **Camera Discovery**
   - RTSP discovery service
   - Camera capability detection
   - Automatic configuration

2. **Camera Controls**
   - Start/stop streaming
   - Settings management
   - Status monitoring

3. **Configuration Management**
   - System settings UI
   - Detection/recognition parameters
   - Performance tuning

### Phase 5: Streaming Implementation (Week 8-9)
1. **WebRTC Integration**
   - Signaling server
   - Peer connection management
   - Stream quality control

2. **RTSP Converter Service**
   - FFmpeg integration
   - Stream transcoding
   - Multi-format support

3. **Fallback Mechanisms**
   - WebSocket streaming
   - Quality adaptation
   - Error recovery

### Phase 6: Real-time Overlays (Week 10-11)
1. **Overlay System**
   - Canvas-based rendering
   - Detection box overlays
   - Recognition labels

2. **Toggleable Controls**
   - Overlay configuration UI
   - Real-time toggle functionality
   - Performance optimization

3. **Advanced Overlays**
   - Pose estimation visualization
   - Tracking trails
   - Debug information

### Phase 7: Person Management (Week 12)
1. **Onboarding System**
   - Photo capture interface
   - Multi-pose capture
   - Embedding generation

2. **Person Database**
   - Person listing and search
   - Edit/delete operations
   - Bulk management

### Phase 8: System Monitoring (Week 13)
1. **Health Monitoring**
   - Service status dashboard
   - Performance metrics
   - Alert system

2. **System Controls**
   - Database reset functionality
   - Service restart controls
   - Log viewing

### Phase 9: Testing & Optimization (Week 14-15)
1. **Testing**
   - Unit tests for all components
   - Integration testing
   - Load testing (5 concurrent users)

2. **Performance Optimization**
   - Frontend bundle optimization
   - Database query optimization
   - Memory and CPU profiling

3. **Documentation**
   - API documentation
   - User guides
   - Deployment instructions

## Technology Stack

### Backend Technologies
- **Framework**: Flask 2.3+
- **GraphQL**: Graphene-Flask
- **Database**: PostgreSQL 15+ with SQLAlchemy
- **Real-time**: Flask-SocketIO
- **Authentication**: PyJWT + bcrypt
- **Message Queue**: kafka-python
- **Caching**: Redis
- **Testing**: pytest, pytest-flask
- **Documentation**: Sphinx

### Frontend Technologies
- **Framework**: React 18+
- **State Management**: React Context + useReducer
- **GraphQL Client**: Apollo Client
- **Real-time**: Socket.IO-client
- **Streaming**: WebRTC APIs
- **Styling**: CSS Modules + Tailwind CSS
- **Build Tool**: Webpack 5
- **Testing**: Jest + React Testing Library

### Infrastructure Technologies
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Kubernetes
- **Service Mesh**: Istio (optional)
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack
- **CI/CD**: GitHub Actions

### Streaming Technologies
- **WebRTC**: Native WebRTC APIs
- **RTSP**: FFmpeg for conversion
- **Signaling**: Socket.IO for WebRTC signaling
- **Video Processing**: OpenCV (Python)

## Success Metrics

### Performance Targets
- **Concurrent Users**: 5 users simultaneously
- **Stream Latency**: < 500ms for WebRTC, < 1s for fallback
- **API Response Time**: < 200ms for GraphQL queries
- **Real-time Updates**: < 100ms for overlay updates
- **System Uptime**: 99.9% availability

### Functional Requirements
- Support for 500+ cameras (discovery and management)
- All overlay types toggleable in real-time
- Complete person onboarding workflow
- Comprehensive system monitoring
- Mobile-responsive design (desktop-optimized)

This comprehensive architecture provides a solid foundation for implementing a scalable, feature-rich GUI service that meets all specified requirements while maintaining flexibility for future enhancements.
