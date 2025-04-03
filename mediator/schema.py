import graphene
from graphene_django import DjangoObjectType
from .gql_mutation import CreateEMRClaim


class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="stranger"))
    def resolve_hello(root, info, name):
        print("api is called")
        return f"Hello, {name}!"
class Mutation(graphene.ObjectType):
    emrClaim = CreateEMRClaim.Field()