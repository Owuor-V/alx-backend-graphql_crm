import logging
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/crm_heartbeat_log.txt"

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
