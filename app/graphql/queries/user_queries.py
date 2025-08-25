# gui-service/app/graphql/queries/user_queries.py

from graphene import ObjectType, ID, String, DateTime
from app.models.user import User

class UserType(ObjectType):
    id = ID()
    username = String()
    role = String()  # Add role field to match User model and Login mutation
    created_at = DateTime()