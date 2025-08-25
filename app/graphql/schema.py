# gui-service/app/graphql/schema.py

from graphene import ObjectType, Schema, Field, List, ID, String, Int, Float, Boolean, DateTime, JSONString
from app.graphql.queries.camera_queries import CameraType, ResolutionType, GetCameras, GetCameraDetails
from app.graphql.queries.person_queries import PersonType, GetPersons
from app.graphql.queries.system_queries import SystemConfigType, SystemStatusType, PerformanceType, ServiceType, GetSystemConfig, GetSystemStatus
from app.graphql.mutations.auth_mutations import Login
from app.graphql.mutations.camera_mutations import AddCamera, UpdateCameraSettings, StartCamera, StopCamera
from app.graphql.mutations.person_mutations import AddPerson

class Query(ObjectType):
    cameras = Field(List(CameraType))
    camera = Field(CameraType, id=ID(required=True))
    persons = Field(List(PersonType))
    system_config = Field(SystemConfigType)
    system_status = Field(SystemStatusType)

    def resolve_cameras(root, info):
        return GetCameras.resolve_cameras(root, info)

    def resolve_camera(root, info, id):
        return GetCameraDetails.resolve_camera(root, info, id)

    def resolve_persons(root, info):
        return GetPersons.resolve_persons(root, info)

    def resolve_system_config(root, info):
        return GetSystemConfig.resolve_system_config(root, info)

    def resolve_system_status(root, info):
        return GetSystemStatus.resolve_system_status(root, info)

class Mutation(ObjectType):
    login = Login.Field()
    add_camera = AddCamera.Field()
    update_camera_settings = UpdateCameraSettings.Field()
    start_camera = StartCamera.Field()
    stop_camera = StopCamera.Field()
    add_person = AddPerson.Field()
    # Add more as needed