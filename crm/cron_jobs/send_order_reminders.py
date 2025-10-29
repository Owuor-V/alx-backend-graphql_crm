#!/usr/bin/env python3
import logging
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configure logging
LOG_FILE = "/tmp/order_reminders_log.txt"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - Order ID: %(message)s"
)


def fetch_pending_orders():
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        use_json=True,
    )

    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql("""
        query GetOrders($startDate: Date!) {
            orders(orderDate_Gte: $startDate) {
                id
                customerEmail
            }
        }
    """)

    # Get today's date - 7 days
    start_date = (datetime.now() - timedelta(days=7)).date().isoformat()

    result = client.execute(query, variable_values={"startDate": start_date})
    return result.get("orders", [])


def main():
    orders = fetch_pending_orders()

    for order in orders:
        order_id = order.get("id")
        customer_email = order.get("customerEmail")
        if order_id and customer_email:
            logging.info(f"{order_id} - {customer_email}")

    print("Order reminders processed!")


if __name__ == "__main__":
    main()
