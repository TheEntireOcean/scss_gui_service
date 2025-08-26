# app/api/system/serializers.py
from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.system_config import SystemConfig

class SystemConfigSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = SystemConfig
        load_instance = True
    
    id = fields.Int(dump_only=True)
    key = fields.Str()
    value = fields.Raw()
    category = fields.Str()
    updated_at = fields.DateTime(data_key='updatedAt')
    updated_by = fields.Int(data_key='updatedBy')

class ServiceSchema(Schema):
    name = fields.Str()
    status = fields.Str()
    health = fields.Str()

class PerformanceSchema(Schema):
    cpu_usage = fields.Float(data_key='cpuUsage')
    memory_usage = fields.Float(data_key='memoryUsage')
    gpu_usage = fields.Float(data_key='gpuUsage')
    disk_usage = fields.Float(data_key='diskUsage')

class SystemStatusSchema(Schema):
    services = fields.List(fields.Nested(ServiceSchema))
    performance = fields.Nested(PerformanceSchema)
    timestamp = fields.Int()