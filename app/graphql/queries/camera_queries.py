# gui-service/app/graphql/queries/camera_queries.py

from graphene import ObjectType, Field, List, ID, String, Int, Boolean, DateTime
from graphene.types.json import JSONString
from app.models.camera import Camera

class ResolutionType(ObjectType):
    width = Int()
    height = Int()

class CameraType(ObjectType):
    id = ID()
    name = String()
    source = String()
    type = String(name='type')
    status = String()
    resolution = Field(ResolutionType)
    fps = Int()
    settings = JSONString()
    is_active = Boolean(name='isActive')
    created_at = DateTime(name='createdAt')
    updated_at = DateTime(name='updatedAt')

class GetCameras(ObjectType):
    @staticmethod
    def resolve_cameras(root, info):
        return Camera.query.all()

class GetCameraDetails(ObjectType):
    @staticmethod
    def resolve_camera(root, info, id):
        return Camera.query.get(id)