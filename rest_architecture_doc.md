# GUI Service - Technical Architecture & Implementation Plan

**Version**: 2.0  
**Date**: August 26, 2025  
**Target**: Scalable Face Recognition System - GUI Component

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Backend Implementation Plan](#backend-implementation-plan)
4. [Frontend Implementation Plan](#frontend-implementation-plan)
5. [Database Schema](#database-schema)
6. [REST API Specifications](#rest-api-specifications)
7. [Real-time Communication](#real-time-communication)
8. [Streaming Architecture](#streaming-architecture)
9. [Security Implementation](#security-implementation)
10. [Deployment Strategy](#deployment-strategy)
11. [Development Phases](#development-phases)
12. [Technology Stack](#technology-stack)

## Executive Summary

The GUI Service is implemented as a full-stack application comprising:
- **Backend**: Flask application with RESTful API, SocketIO, and direct PostgreSQL integration
- **Frontend**: React SPA with real-time streaming, overlays, and comprehensive camera management
- **Streaming**: Multi-tier streaming architecture (WebRTC → RTSP conversion → WebSocket fallback)
- **Authentication**: JWT-based authentication with role-based access control
- **Real-time**: Kafka message forwarding service with WebSocket distribution

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GUI Service Architecture              │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React)                                               │
│  ├── Camera Dashboard (Single + Thumbnails)                     │
│  ├── Real-time Overlays (Toggleable)                           │
│  ├── Configuration Management                                   │
│  └── Person Management (Onboarding)                            │
├─────────────────────────────────────────────────────────────────┤
│  Backend (Flask)                                                │
│  ├── REST API with Flask-RESTful                               │
│  ├── Blueprint-based Route Organization                        │
│  ├── JWT Authentication Middleware                             │
│  ├── Request/Response Serialization (Marshmallow)              │
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
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── serializers.py
│   │   ├── cameras/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── serializers.py
│   │   ├── persons/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── serializers.py
│   │   ├── system/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── serializers.py
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── validation.py
│   │       └── error_handlers.py
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
│   │   ├── validators.py
│   │   └── response_helpers.py
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

#### 1. REST API Structure

```python
# Authentication Blueprint
from flask import Blueprint
from flask_restful import Api, Resource

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
auth_api = Api(auth_bp)

class LoginResource(Resource):
    def post(self):
        """User login endpoint"""
        pass

class LogoutResource(Resource):
    def post(self):
        """User logout endpoint"""
        pass

class ProfileResource(Resource):
    def get(self):
        """Get current user profile"""
        pass

auth_api.add_resource(LoginResource, '/login')
auth_api.add_resource(LogoutResource, '/logout')
auth_api.add_resource(ProfileResource, '/profile')
```

#### 2. Serialization Layer with Marshmallow

```python
# Camera Serializers
from marshmallow import Schema, fields, validate, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class CameraSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Camera
        load_instance = True
    
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    source = fields.Str(required=True, validate=validate.Regexp(r'^(rtsp://|http://|/dev/)'))
    camera_type = fields.Str(required=True, validate=validate.OneOf(['rtsp', 'webcam', 'usb']))
    resolution = fields.Nested('ResolutionSchema', dump_only=True)
    is_active = fields.Bool(dump_only=True, data_key='isActive')
    created_at = fields.DateTime(dump_only=True, data_key='createdAt')
    updated_at = fields.DateTime(dump_only=True, data_key='updatedAt')

class ResolutionSchema(Schema):
    width = fields.Int()
    height = fields.Int()

class CameraCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    source = fields.Str(required=True, validate=validate.Regexp(r'^(rtsp://|http://|/dev/)'))
    camera_type = fields.Str(required=True, validate=validate.OneOf(['rtsp', 'webcam', 'usb']))
    
class CameraUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=255))
    source = fields.Str(validate=validate.Regexp(r'^(rtsp://|http://|/dev/)'))
    settings = fields.Raw()
```

#### 3. Authentication Middleware

```python
from functools import wraps
from flask import request, current_app
from flask_restful import abort
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                abort(401, message="Invalid token format")
        
        if not token:
            abort(401, message="Token is missing")
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['user_id']).first()
            if not current_user:
                abort(401, message="Invalid token")
        except jwt.ExpiredSignatureError:
            abort(401, message="Token has expired")
        except jwt.InvalidTokenError:
            abort(401, message="Invalid token")
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            abort(403, message="Admin access required")
        return f(current_user, *args, **kwargs)
    return decorated
```

#### 4. Response Helper Functions

```python
def success_response(data=None, message=None, status_code=200):
    response = {'success': True}
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    return response, status_code

def error_response(message, code=None, details=None, status_code=400):
    response = {
        'success': False,
        'error': {
            'message': message
        }
    }
    if code:
        response['error']['code'] = code
    if details:
        response['error']['details'] = details
    return response, status_code

def paginated_response(items, page, per_page, total, endpoint=None):
    return {
        'success': True,
        'data': items,
        'pagination': {
            'page': page,
            'pages': math.ceil(total / per_page),
            'per_page': per_page,
            'total': total,
            'has_next': page * per_page < total,
            'has_prev': page > 1
        }
    }
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
│   ├── services/
│   │   ├── api/
│   │   │   ├── client.js
│   │   │   ├── auth.js
│   │   │   ├── cameras.js
│   │   │   ├── persons.js
│   │   │   └── system.js
│   │   ├── streaming/
│   │   │   ├── webrtc-client.js
│   │   │   ├── websocket-client.js
│   │   │   └── stream-manager.js
│   │   └── socket.js
│   ├── hooks/
│   │   ├── useAPI.js
│   │   ├── useSocket.js
│   │   ├── useAuth.js
│   │   ├── useCamera.js
│   │   └── useRealtime.js
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

#### 1. API Service Layer
```javascript
// API Client Setup
import axios from 'axios';

class APIClient {
  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      timeout: 10000,
    });
    
    // Request interceptor for auth
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
    
    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response.data,
      (error) => {
        if (error.response?.status === 401) {
          // Handle token expiration
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }
  
  async get(url, params = {}) {
    return this.client.get(url, { params });
  }
  
  async post(url, data = {}) {
    return this.client.post(url, data);
  }
  
  async put(url, data = {}) {
    return this.client.put(url, data);
  }
  
  async delete(url) {
    return this.client.delete(url);
  }
}

export default new APIClient();
```

#### 2. Camera Service
```javascript
// cameras.js
import apiClient from './client';

export const cameraService = {
  async getCameras(page = 1, per_page = 20) {
    return apiClient.get('/cameras', { page, per_page });
  },
  
  async getCamera(id) {
    return apiClient.get(`/cameras/${id}`);
  },
  
  async createCamera(data) {
    return apiClient.post('/cameras', data);
  },
  
  async updateCamera(id, data) {
    return apiClient.put(`/cameras/${id}`, data);
  },
  
  async deleteCamera(id) {
    return apiClient.delete(`/cameras/${id}`);
  },
  
  async startCamera(id) {
    return apiClient.post(`/cameras/${id}/start`);
  },
  
  async stopCamera(id) {
    return apiClient.post(`/cameras/${id}/stop`);
  },
  
  async updateCameraSettings(id, settings) {
    return apiClient.put(`/cameras/${id}/settings`, settings);
  },
  
  async discoverCameras() {
    return apiClient.get('/cameras/discover');
  }
};
```

#### 3. Custom Hooks
```javascript
// useCamera.js
import { useState, useEffect } from 'react';
import { cameraService } from '../services/api/cameras';

export const useCamera = (id) => {
  const [camera, setCamera] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    if (id) {
      loadCamera(id);
    }
  }, [id]);
  
  const loadCamera = async (cameraId) => {
    try {
      setLoading(true);
      setError(null);
      const response = await cameraService.getCamera(cameraId);
      setCamera(response.data.camera);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load camera');
    } finally {
      setLoading(false);
    }
  };
  
  const startCamera = async () => {
    try {
      await cameraService.startCamera(id);
      setCamera(prev => ({ ...prev, status: 'active', isActive: true }));
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to start camera');
    }
  };
  
  const stopCamera = async () => {
    try {
      await cameraService.stopCamera(id);
      setCamera(prev => ({ ...prev, status: 'inactive', isActive: false }));
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to stop camera');
    }
  };
  
  return {
    camera,
    loading,
    error,
    startCamera,
    stopCamera,
    refetch: () => loadCamera(id)
  };
};
```

## Database Schema

### Extended PostgreSQL Schema (Unchanged)

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

## REST API Specifications

### Authentication Endpoints

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

Response (200):
{
  "success": true,
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "role": "admin"
    }
  }
}
```

```http
POST /api/auth/logout
Authorization: Bearer <token>

Response (200):
{
  "success": true,
  "message": "Logged out successfully"
}
```

```http
GET /api/auth/profile
Authorization: Bearer <token>

Response (200):
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "admin",
      "role": "admin",
      "createdAt": "2025-08-26T10:00:00Z",
      "lastLogin": "2025-08-26T12:00:00Z"
    }
  }
}
```

### Camera Management Endpoints

```http
GET /api/cameras?page=1&per_page=20&status=active
Authorization: Bearer <token>

Response (200):
{
  "success": true,
  "data": {
    "cameras": [
      {
        "id": 1,
        "name": "Front Door Camera",
        "source": "rtsp://192.168.1.100:554/stream",
        "type": "rtsp",
        "status": "active",
        "resolution": {
          "width": 1920,
          "height": 1080
        },
        "fps": 30,
        "settings": {
          "brightness": 50,
          "contrast": 50
        },
        "isActive": true,
        "createdAt": "2025-08-26T10:00:00Z",
        "updatedAt": "2025-08-26T12:00:00Z"
      }
    ]
  },
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 20,
    "total": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

```http
POST /api/cameras
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "New Camera",
  "source": "rtsp://192.168.1.101:554/stream",
  "camera_type": "rtsp"
}

Response (201):
{
  "success": true,
  "data": {
    "camera": {
      "id": 2,
      "name": "New Camera",
      "source": "rtsp://192.168.1.101:554/stream",
      "type": "rtsp",
      "status": "inactive",
      "isActive": false,
      "createdAt": "2025-08-26T12:30:00Z"
    }
  }
}
```

```http
PUT /api/cameras/1/settings
Authorization: Bearer <token>
Content-Type: application/json

{
  "resolution_width": 1920,
  "resolution_height": 1080,
  "fps": 25,
  "settings": {
    "brightness": 60,
    "contrast": 45
  }
}

Response (200):
{
  "success": true,
  "data": {
    "camera": {
      "id": 1,
      "settings": {
        "brightness": 60,
        "contrast": 45
      },
      "fps": 25
    }
  }
}
```

```http
POST /api/cameras/1/start
Authorization: Bearer <token>

Response (200):
{
  "success": true,
  "data": {
    "camera": {
      "id": 1,
      "status": "active",
      "isActive": true
    }
  }
}
```

```http
GET /api/cameras/discover
Authorization: Bearer <token>

Response (200):
{
  "success": true,
  "data": {
    "discovered_cameras": [
      {
        "source": "rtsp://192.168.1.102:554/stream",
        "name": "Discovered Camera 1",
        "type": "rtsp",
        "capabilities": {
          "resolutions": ["1920x1080", "1280x720"],
          "fps_options": [30, 25, 15]
        }
      }
    ]
  }
}
```

### Person Management Endpoints

```http
GET /api/persons?page=1&per_page=20&search=john
Authorization: Bearer <token>

Response (200):
{
  "success": true,
  "data": {
    "persons": [
      {
        "id": 1,
        "name": "John Doe",
        "images": [
          "/uploads/persons/1/image1.jpg",
          "/uploads/persons/1/image2.jpg"
        ],
        "lastSeen": "2025-08-26T11:30:00Z",
        "confidence": 0.95,
        "createdAt": "2025-08-26T10:00:00Z"
      }
    ]
  },
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 20,
    "total": 1
  }
}
```

```http
POST /api/persons
Authorization: Bearer <token>
Content-Type: multipart/form-data

name: Jane Smith
images: [file1.jpg, file2.jpg]

Response (201):
{
  "success": true,
  "data": {
    "person": {
      "id": 2,
      "name": "Jane Smith",
      "images": [
        "/uploads/persons/2/image1.jpg",
        "/uploads/persons/2/image2.jpg"
      ],
      "createdAt": "2025-08-26T12:30:00Z"
    }
  }
}
```

### System Management Endpoints

```http
GET /api/system/config
Authorization: Bearer <token>

Response (200):
{
  "success": true,
  "data": {
    "config": {
      "detectionThreshold": 0.5,
      "recognitionConfidence": 0.8,
      "samplingRate": 30,
      "performanceMode": "balanced"
    }
  }
}
```

```http
PUT /api/system/config
Authorization: Bearer <token>
Content-Type: application/json

{
  "detectionThreshold": 0.6,
  "recognitionConfidence": 0.85,
  "performanceMode": "high_accuracy"
}

Response (200):
{
  "success": true,
  "data": {
    "config": {
      "detectionThreshold": 0.6,
      "recognitionConfidence": 0.85,
      "samplingRate": 30,
      "performanceMode": "high_accuracy"
    }
  }
}
```

```http
GET /api/system/status
Authorization: Bearer <token>

Response (200):
{
  "success": true,
  "data": {
    "services": [
      {
        "name": "gui-service",
        "status": "running",
        "health": "healthy"
      },
      {
        "name": "detection-service",
        "status": "running",
        "health": "healthy"
      }
    ],
    "performance": {
      "cpuUsage": 25.5,
      "memoryUsage": 68.2,
      "gpuUsage": 45.0,
      "diskUsage": 23.1
    },
    "timestamp": 1693051200
  }
}
```

### Error Response Format

```http
Response (400):
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "name": ["This field is required"],
      "source": ["Invalid RTSP URL format"]
    }
  }
}

Response (401):
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Token has expired"
  }
}

Response (404):
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Camera not found"
  }
}

Response (500):
{
  "success": false,
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred"
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
# REST input validation with Marshmallow
class CameraCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    source = fields.Str(required=True, validate=validate.Regexp(r'^(rtsp://|http://|/dev/)'))
    camera_type = fields.Str(required=True, validate=validate.OneOf(['rtsp', 'webcam', 'usb']))
    
    @post_load
    def make_camera(self, data, **kwargs):
        return Camera(**data)
    
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


2. **REST API Implementation**
   - Blueprint and route organization
   - Resource classes and endpoints
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
- **REST API**: Flask-RESTful
- **Serialization**: Marshmallow
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
- **API Client**: Axios
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
- **API Response Time**: < 200ms for REST endpoints
- **Real-time Updates**: < 100ms for overlay updates
- **System Uptime**: 99.9% availability

### Functional Requirements
- Support for 500+ cameras (discovery and management)
- All overlay types toggleable in real-time
- Complete person onboarding workflow
- Comprehensive system monitoring
- Mobile-responsive design (desktop-optimized)

This comprehensive architecture provides a solid foundation for implementing a scalable, feature-rich GUI service that meets all specified requirements while maintaining flexibility for future enhancements.
