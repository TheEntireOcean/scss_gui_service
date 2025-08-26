# app/api/persons/serializers.py
from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.person import Person

class PersonSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Person
        load_instance = True
    
    id = fields.Int(dump_only=True)
    name = fields.Str()
    images = fields.List(fields.Str())
    last_seen = fields.DateTime(data_key='lastSeen')
    confidence = fields.Float()
    created_at = fields.DateTime(data_key='createdAt')

class PersonCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    images = fields.List(fields.Str(), missing=[])