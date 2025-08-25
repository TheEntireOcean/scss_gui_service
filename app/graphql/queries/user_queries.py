# app/graphql/queries/user_queries.py

from graphene import ObjectType, ID, String, DateTime
from app.models.user import User

class UserType(ObjectType):
    id = ID()
    username = String()
    email = String()
    created_at = DateTime()
