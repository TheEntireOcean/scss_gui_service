# gui-service/app/graphql/queries/system_queries.py

from graphene import ObjectType, Float, Int, String, List, Field

class SystemConfigType(ObjectType):
    detection_threshold = Float(name='detectionThreshold')
    recognition_confidence = Float(name='recognitionConfidence')
    sampling_rate = Int(name='samplingRate')
    performance_mode = String(name='performanceMode')

class ServiceType(ObjectType):
    name = String()
    status = String()
    health = String()

class PerformanceType(ObjectType):
    cpu_usage = Float(name='cpuUsage')
    memory_usage = Float(name='memoryUsage')
    gpu_usage = Float(name='gpuUsage')

class SystemStatusType(ObjectType):
    services = List(ServiceType)
    performance = Field(PerformanceType)

class GetSystemConfig(ObjectType):
    @staticmethod
    def resolve_system_config(root, info):
        # Placeholder: Fetch from DB
        return {
            'detectionThreshold': 0.5,
            'recognitionConfidence': 0.8,
            'samplingRate': 30,
            'performanceMode': 'balanced'
        }

class GetSystemStatus(ObjectType):
    @staticmethod
    def resolve_system_status(root, info):
        # Placeholder: Implement actual status fetching
        return {
            'services': [
                {'name': 'backend', 'status': 'running', 'health': 'healthy'}
            ],
            'performance': {
                'cpuUsage': 20.5,
                'memoryUsage': 45.0,
                'gpuUsage': 10.0
            }
        }