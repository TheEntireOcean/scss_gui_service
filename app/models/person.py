# gui-service/app/models/person.py

from app import db
from datetime import datetime

class Person(db.Model):
    __tablename__ = 'persons'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    images = db.Column(db.ARRAY(db.Text), default=list)
    person_metadata = db.Column(db.JSON, default=dict)  # renamed from 'metadata'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen = db.Column(db.DateTime)

class Embedding(db.Model):
    __tablename__ = 'embeddings'
    
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('persons.id', ondelete='CASCADE'))
    embedding = db.Column(db.LargeBinary, nullable=False)
    image_path = db.Column(db.String(500))
    confidence = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)