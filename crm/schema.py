import graphene
from graphene import Field, List, String, Int, Float, Boolean, Mutation, InputObjectType
from graphene_django import DjangoObjectType
from django.core.exceptions import ValidationError
from django.db import transaction
from models import Customer, Product, Order
import re
from django.utils import timezone

# --- Types ---
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")

# --- Inputs ---
class CustomerInput(InputObjectType):
    name = String(required=True)
    email = String(required=True)
    phone = String()

class ProductInput(InputObjectType):
    name = String(required=True)
    price = Float(required=True)
    stock = Int()

class OrderInput(InputObjectType):
    customer_id = Int(required=True)
    product_ids = List(Int, required=True)
    order_date = String()

# --- Mutations ---
class CreateCustomer(Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = Field(CustomerType)
    message = String()
    success = Boolean()
    errors = List(String)

    @classmethod
    def validate_phone(cls, phone):
        if not phone:
            return True
        pattern = r"^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$"
        return re.match(pattern, phone)

    @classmethod
    def mutate(cls, root, info, input):
        errors = []
        if not cls.validate_phone(input.get("phone")):
            errors.append("Invalid phone format.")
        if Customer.objects.filter(email=input["email"]).exists():
            errors.append("Email already exists.")
        if errors:
            return CreateCustomer(customer=None, message="Validation failed.", success=False, errors=errors)
        customer = Customer.objects.create(
            name=input["name"],
            email=input["email"],
            phone=input.get("phone", "")
        )
        return CreateCustomer(customer=customer, message="Customer created successfully.", success=True, errors=[])

class BulkCreateCustomers(Mutation):
    class Arguments:
        input = List(CustomerInput, required=True)

    customers = List(CustomerType)
    errors = List(String)
    success = Boolean()

    @classmethod
    def mutate(cls, root, info, input):
        created = []
        errors = []
        with transaction.atomic():
            for idx, data in enumerate(input):
                err = []
                if not CreateCustomer.validate_phone(data.get("phone")):
                    err.append(f"[{idx}] Invalid phone format.")
                if Customer.objects.filter(email=data["email"]).exists():
                    err.append(f"[{idx}] Email already exists.")
                if err:
                    errors.extend(err)
                    continue
                customer = Customer.objects.create(
                    name=data["name"],
                    email=data["email"],
                    phone=data.get("phone", "")
                )
                created.append(customer)
        return BulkCreateCustomers(customers=created, errors=errors, success=len(errors) == 0)

class CreateProduct(Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = Field(ProductType)
    errors = List(String)
    success = Boolean()

    @classmethod
    def mutate(cls, root, info, input):
        errors = []
        if input["price"] <= 0:
            errors.append("Price must be positive.")
        if input.get("stock", 0) < 0:
            errors.append("Stock cannot be negative.")
        if errors:
            return CreateProduct(product=None, errors=errors, success=False)
        product = Product.objects.create(
            name=input["name"],
            price=input["price"],
            stock=input.get("stock", 0)
        )
        return CreateProduct(product=product, errors=[], success=True)

class CreateOrder(Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = Field(OrderType)
    errors = List(String)
    success = Boolean()

    @classmethod
    def mutate(cls, root, info, input):
        errors = []
        try:
            customer = Customer.objects.get(id=input["customer_id"])
        except Customer.DoesNotExist:
            errors.append("Invalid customer ID.")
            return CreateOrder(order=None, errors=errors, success=False)
        products = Product.objects.filter(id__in=input["product_ids"])
        if products.count() != len(input["product_ids"]):
            errors.append("One or more product IDs are invalid.")
        if not products:
            errors.append("At least one product must be selected.")
        if errors:
            return CreateOrder(order=None, errors=errors, success=False)
        order_date = input.get("order_date")
        if order_date:
            try:
                order_date = timezone.datetime.fromisoformat(order_date)
            except Exception:
                order_date = timezone.now()
        else:
            order_date = timezone.now()
        total_amount = sum([float(p.price) for p in products])
        order = Order.objects.create(
            customer=customer,
            order_date=order_date,
            total_amount=total_amount
        )
        order.products.set(products)
        return CreateOrder(order=order, errors=[], success=True)

# --- Register Mutations ---
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

    # Register the mutation in the schema. Graphene will expose it as `updateLowStockProducts`.
    update_low_stock_products = UpdateLowStockProducts.Field()


schema = graphene.Schema(mutation=Mutation)
