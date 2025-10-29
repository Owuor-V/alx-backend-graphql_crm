# crm/schema.py
import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter
from crm.models import Product


class UpdateLowStockProducts(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(graphene.String)

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)

        updated_names = []
        for product in low_stock_products:
            product.stock += 10  # Simulate restocking
            product.save()
            updated_names.append(f"{product.name} (Stock: {product.stock})")

        if not updated_names:
            return UpdateLowStockProducts(
                success=True,
                message="No low-stock products to update.",
                updated_products=[]
            )

        return UpdateLowStockProducts(
            success=True,
            message="Low-stock products successfully updated!",
            updated_products=updated_names
        )


class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        interfaces = (graphene.relay.Node,)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, order_by=graphene.String())
    all_products = DjangoFilterConnectionField(ProductType, order_by=graphene.String())
    all_orders = DjangoFilterConnectionField(OrderType, order_by=graphene.String())

    def resolve_all_customers(self, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        if order_by:
            qs = qs.order_by(order_by)
        return qs

    def resolve_all_products(self, info, order_by=None, **kwargs):
        qs = Product.objects.all()
        if order_by:
            qs = qs.order_by(order_by)
        return qs

    def resolve_all_orders(self, info, order_by=None, **kwargs):
        qs = Order.objects.all()
        if order_by:
            qs = qs.order_by(order_by)
        return qs
