import graphene


class Query(graphene.ObjectType):
    """Root GraphQL query for the project."""

    hello = graphene.String(description="A simple hello world field")

    def resolve_hello(self, info):
        return "Hello, GraphQL!"


schema = graphene.Schema(query=Query)
