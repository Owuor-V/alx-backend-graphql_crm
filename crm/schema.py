import re
import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.db import transaction
from django.utils import timezone
from .models import Customer, Product, Order


# --------------------------
# GraphQL Object Types
# --------------------------
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


# --------------------------
# Input Object Definitions
# --------------------------
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(required=False, default_value=0)


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.NonNull(graphene.ID), required=True)
    order_date = graphene.DateTime(required=False)


# --------------------------
# Mutation: Create Customer
# --------------------------
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        # Validate unique email
        if Customer.objects.filter(email=input.email).exists():
            raise GraphQLError("Email already exists")

        # Validate phone format if provided
        if input.phone and not re.match(r"^\+?\d[\d\-]{7,14}$", input.phone):
            raise GraphQLError("Invalid phone format. Use +1234567890 or 123-456-7890")

        customer = Customer.objects.create(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        return CreateCustomer(customer=customer, message="Customer created successfully ✅")


# --------------------------
# Mutation: Bulk Create Customers
# --------------------------
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        created_customers = []
        errors = []

        for data in input:
            try:
                # Check if email already exists
                if Customer.objects.filter(email=data.email).exists():
                    raise GraphQLError(f"Email already exists: {data.email}")

                # Validate phone format if provided
                if data.phone and not re.match(r"^\+?\d[\d\-]{7,14}$", data.phone):
                    raise GraphQLError(f"Invalid phone format for {data.name}")

                customer = Customer.objects.create(
                    name=data.name,
                    email=data.email,
                    phone=data.phone
                )
                created_customers.append(customer)

            except GraphQLError as e:
                errors.append(str(e))
            except Exception as e:
                errors.append(f"Unexpected error for {data.name}: {e}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)


# --------------------------
# Mutation: Create Product
# --------------------------
class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise GraphQLError("Price must be positive")
        if input.stock < 0:
            raise GraphQLError("Stock cannot be negative")

        product = Product.objects.create(
            name=input.name,
            price=input.price,
            stock=input.stock or 0
        )
        return CreateProduct(product=product)


# --------------------------
# Mutation: Create Order
# --------------------------
class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        # Validate customer existence
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise GraphQLError("Invalid customer ID")

        # Validate product list
        if not input.product_ids:
            raise GraphQLError("At least one product must be provided")

        products = Product.objects.filter(id__in=input.product_ids)
        if not products.exists():
            raise GraphQLError("Invalid product IDs")

        # Calculate total amount accurately
        total_amount = sum(p.price for p in products)
        order_date = input.order_date or timezone.now()

        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=order_date
        )
        order.products.set(products)

        return CreateOrder(order=order)


# --------------------------
# Root Query
# --------------------------
class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    def resolve_all_customers(root, info):
        return Customer.objects.all()

    def resolve_all_products(root, info):
        return Product.objects.all()

    def resolve_all_orders(root, info):
        return Order.objects.all()


# --------------------------
# Root Mutation
# --------------------------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
