# alx_backend_graphql_crm/schema.py
import graphene
import crm.schema

class Query(crm.schema.Query, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)
