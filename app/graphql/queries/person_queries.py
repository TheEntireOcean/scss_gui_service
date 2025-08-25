# gui-service/app/graphql/queries/person_queries.py

from graphene import ObjectType, List, ID, String, DateTime, Float
from app.models.person import Person

class PersonType(ObjectType):
    id = ID()
    name = String()
    images = List(String)
    last_seen = DateTime(name='lastSeen')
    confidence = Float()
    created_at = DateTime(name='createdAt')  # Add createdAt field to match Person model

class GetPersons(ObjectType):
    @staticmethod
    def resolve_persons(root, info):
        return Person.query.all()