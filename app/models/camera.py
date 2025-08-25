# gui-service/app/models/camera.py

from app import db
from datetime import datetime

class Camera(db.Model):
    __tablename__ = 'cameras'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    source = db.Column(db.String(500), nullable=False)
    camera_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='inactive')
    resolution_width = db.Column(db.Integer, default=1920)
    resolution_height = db.Column(db.Integer, default=1080)
    fps = db.Column(db.Integer, default=30)
    settings = db.Column(db.JSON, default=dict)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)