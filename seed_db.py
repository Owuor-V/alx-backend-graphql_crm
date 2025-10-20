import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product

# Clear existing data
Customer.objects.all().delete()
Product.objects.all().delete()

# Seed sample data
customers = [
    {"name": "Alice", "email": "alice@example.com", "phone": "+1234567890"},
    {"name": "Bob", "email": "bob@example.com", "phone": "123-456-7890"},
]

for c in customers:
    Customer.objects.create(**c)

products = [
    {"name": "Laptop", "price": 999.99, "stock": 10},
    {"name": "Mouse", "price": 25.50, "stock": 100},
]

for p in products:
    Product.objects.create(**p)

print("Database seeded successfully ✅")
