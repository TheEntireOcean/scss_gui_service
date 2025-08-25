# gui-service/app/graphql/mutations/auth_mutations.py

from graphene import Mutation, String, Field
from app.services.auth_service import AuthService
from app.graphql.queries.user_queries import UserType


class Login(Mutation):
    class Arguments:
        username = String(required=True)
        password = String(required=True)

    token = String()
    user = Field(UserType)

    def mutate(root, info, username, password):
        auth_service = AuthService()
        result = auth_service.authenticate(username, password)
        if result:
            return Login(token=result['token'], user=result['user'])
        return None