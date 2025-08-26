from marshmallow import Schema, fields, validate, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.user import User

class LoginSchema(Schema):
    """Schema for user login"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    password = fields.Str(required=True, validate=validate.Length(min=6))

class UserSchema(SQLAlchemyAutoSchema):
    """Schema for user data serialization"""
    class Meta:
        model = User
        exclude = ('password_hash',)
        dump_only_fields = ('id', 'created_at', 'last_login')
    
    created_at = fields.DateTime(data_key='createdAt')
    last_login = fields.DateTime(data_key='lastLogin')

class UserCreateSchema(Schema):
    """Schema for creating new users"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=255))
    password = fields.Str(required=True, validate=validate.Length(min=6))
    role = fields.Str(validate=validate.OneOf(['admin', 'viewer']), missing='viewer')

class UserUpdateSchema(Schema):
    """Schema for updating user data"""
    username = fields.Str(validate=validate.Length(min=3, max=255))
    role = fields.Str(validate=validate.OneOf(['admin', 'viewer']))
    
class PasswordChangeSchema(Schema):
    """Schema for password change"""
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6))