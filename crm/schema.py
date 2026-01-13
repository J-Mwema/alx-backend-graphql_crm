import graphene

# Define a simple GraphQL type to represent products with a name and stock level
class ProductType(graphene.ObjectType):
    name = graphene.String()
    stock = graphene.Int()


class UpdateLowStockProducts(graphene.Mutation):
    """Mutation that finds products with stock < 10, increases their stock by 10,
    and returns the list of updated products along with a success message.
    """

    class Arguments:
        # No arguments needed for this mutation
        pass

    updated_products = graphene.List(ProductType)
    success = graphene.Boolean()
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info):
        try:
            # Attempt to import the Product model; if not present this will fail gracefully
            from crm.models import Product
            from django.db.models import F

            # Query products with stock < 10
            qs = Product.objects.filter(stock__lt=10)
            updated = []

            # Increment stock for each product and record the new levels
            for p in qs:
                # Use simple save to update stock; for large updates consider queryset.update()
                p.stock = p.stock + 10
                p.save()
                updated.append(ProductType(name=p.name, stock=p.stock))

            return UpdateLowStockProducts(updated_products=updated, success=True, message="Restocked low stock products")
        except Exception as exc:
            # Return a failure message if models or DB are not present
            return UpdateLowStockProducts(updated_products=[], success=False, message=str(exc))


class Mutation(graphene.ObjectType):
    # Register the mutation in the schema. Graphene will expose it as `updateLowStockProducts`.
    update_low_stock_products = UpdateLowStockProducts.Field()


schema = graphene.Schema(mutation=Mutation)
