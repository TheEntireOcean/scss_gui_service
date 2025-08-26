# app/api/cameras/serializers.py
from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.camera import Camera

class ResolutionSchema(Schema):
    width = fields.Int()
    height = fields.Int()

class CameraSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Camera
        load_instance = True
        include_fk = True
    
    id = fields.Int(dump_only=True)
    name = fields.Str()
    source = fields.Str()
    type = fields.Method("get_camera_type")
    status = fields.Str()
    resolution = fields.Method("get_resolution")
    fps = fields.Int()
    settings = fields.Raw()
    is_active = fields.Bool(data_key='isActive')
    created_at = fields.DateTime(data_key='createdAt')
    updated_at = fields.DateTime(data_key='updatedAt')
    
    def get_camera_type(self, obj):
        return obj.camera_type
    
    def get_resolution(self, obj):
        return {
            'width': obj.resolution_width,
            'height': obj.resolution_height
        }

class CameraCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    source = fields.Str(required=True, validate=validate.Regexp(r'^(rtsp://|http://|/dev/)'))
    camera_type = fields.Str(required=True, validate=validate.OneOf(['rtsp', 'webcam', 'usb']))

class CameraUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=255))
    source = fields.Str(validate=validate.Regexp(r'^(rtsp://|http://|/dev/)'))
    camera_type = fields.Str(validate=validate.OneOf(['rtsp', 'webcam', 'usb']))
    settings = fields.Raw()