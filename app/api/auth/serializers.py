# app/api/auth/serializers.py
from marshmallow import Schema, fields, validate

class LoginSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=1))
    password = fields.Str(required=True, validate=validate.Length(min=1))

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()
    role = fields.Str()
    created_at = fields.DateTime(dump_only=True, data_key='createdAt')
    last_login = fields.DateTime(dump_only=True, data_key='lastLogin')