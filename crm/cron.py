import logging
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/crm_heartbeat_log.txt"
LOW_STOCK_LOG_FILE = "/tmp/low_stock_updates_log.txt"
def log_crm_heartbeat():
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"

    # Append log message
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(message)s'
    )
    logging.info(message)

    # Optional GraphQL Health Check
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            use_json=True,
        )
        client = Client(transport=transport, fetch_schema_from_transport=True)

        query = gql("""query { hello }""")
        client.execute(query)  # If fails → exception thrown

    except Exception as e:
        logging.info(f"GraphQL health check failed: {e}")


def update_low_stock():
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        use_json=True,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    mutation = gql("""
        mutation {
            updateLowStockProducts {
                success
                message
                updatedProducts
            }
        }
    """)

    result = client.execute(mutation)
    data = result.get("updateLowStockProducts", {})

    updated_products = data.get("updatedProducts", [])

    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    logging.basicConfig(
        filename=LOW_STOCK_LOG_FILE,
        level=logging.INFO,
        format='%(message)s'
    )

    if updated_products:
        for product_info in updated_products:
            logging.info(f"{timestamp} Updated → {product_info}")
    else:
        logging.info(f"{timestamp} No low-stock products updated")