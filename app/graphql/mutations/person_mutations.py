# gui-service/app/graphql/mutations/person_mutations.py

from graphene import Mutation, Field, InputObjectType, String, List
from app.models.person import Person
from app import db
from app.graphql.queries.person_queries import PersonType

class PersonInput(InputObjectType):
    name = String(required=True)
    images = List(String)

class AddPerson(Mutation):
    class Arguments:
        input = PersonInput(required=True)

    person = Field(PersonType)

    def mutate(root, info, input):
        person = Person(name=input.name, images=input.images or [])
        db.session.add(person)
        db.session.commit()
        return AddPerson(person=person)