import logging
from datetime import datetime
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/crm_report_log.txt"

@shared_task
def generate_crm_report():
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        use_json=True,
    )

    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql("""
        query {
            customersCount
            ordersCount
            totalRevenue
        }
    """)

    result = client.execute(query)

    customers = result.get("customersCount")
    orders = result.get("ordersCount")
    revenue = result.get("totalRevenue")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
    logging.info(
        f"{timestamp} - Report: {customers} customers, {orders} orders, {revenue} revenue"
    )

    return "CRM Report Generated"
