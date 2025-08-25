# gui-service/app/graphql/mutations/camera_mutations.py

from graphene import Mutation, Field, ID, InputObjectType, String, Int, JSONString, Boolean
from app.models.camera import Camera
from app import db
from app.graphql.queries.camera_queries import CameraType

class CameraSettingsInput(InputObjectType):
    # Define fields as per needs
    resolution_width = Int()
    resolution_height = Int()
    fps = Int()
    # Add more

class CameraInput(InputObjectType):
    name = String(required=True)
    source = String(required=True)
    camera_type = String(required=True)
    # Add more optional fields

class AddCamera(Mutation):
    class Arguments:
        input = CameraInput(required=True)

    camera = Field(CameraType)

    def mutate(root, info, input):
        camera = Camera(
            name=input.name,
            source=input.source,
            camera_type=input.camera_type
        )
        db.session.add(camera)
        db.session.commit()
        return AddCamera(camera=camera)

class UpdateCameraSettings(Mutation):
    class Arguments:
        id = ID(required=True)
        settings = CameraSettingsInput(required=True)

    camera = Field(CameraType)

    def mutate(root, info, id, settings):
        camera = Camera.query.get(id)
        if camera:
            # Update settings
            if 'resolution_width' in settings:
                camera.resolution_width = settings.resolution_width
            # Similarly for others
            db.session.commit()
            return UpdateCameraSettings(camera=camera)
        return None

class StartCamera(Mutation):
    class Arguments:
        id = ID(required=True)

    camera = Field(CameraType)

    def mutate(root, info, id):
        camera = Camera.query.get(id)
        if camera:
            camera.status = 'active'
            camera.is_active = True
            db.session.commit()
            return StartCamera(camera=camera)
        return None

class StopCamera(Mutation):
    class Arguments:
        id = ID(required=True)

    camera = Field(CameraType)

    def mutate(root, info, id):
        camera = Camera.query.get(id)
        if camera:
            camera.status = 'inactive'
            camera.is_active = False
            db.session.commit()
            return StopCamera(camera=camera)
        return None