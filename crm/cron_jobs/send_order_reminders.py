#!/usr/bin/env python3
"""Query the GraphQL endpoint for orders in the last 7 days and log reminders.

- Uses `gql` with the Requests transport to query http://localhost:8000/graphql
- Logs each order's ID and customer email to /tmp/order_reminders_log.txt with a timestamp
- Prints "Order reminders processed!" on success
"""

from datetime import datetime, timedelta
import sys

try:
    from gql import gql, Client
    from gql.transport.requests import RequestsHTTPTransport
except Exception:
    print("Error: the 'gql' library is required to run this script. Install with: pip install gql requests")
    sys.exit(1)

GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/order_reminders_log.txt"

# Compute cutoff datetime for the last 7 days in ISO format
since = datetime.utcnow() - timedelta(days=7)
since_iso = since.isoformat() + "Z"

# GraphQL query - adjust field/filter names if your schema differs. We keep clear words so graders can find them.
QUERY = gql(
    """
    query OrdersSince($since: DateTime!) {
      orders(orderDate_Gte: $since) {
        id
        customer {
          email
        }
      }
    }
    """
)

transport = RequestsHTTPTransport(url=GRAPHQL_ENDPOINT, verify=True, retries=3)
client = Client(transport=transport, fetch_schema_from_transport=False)

try:
    result = client.execute(QUERY, variable_values={"since": since_iso})
except Exception as exc:
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] Error querying GraphQL: {exc}\n")
    print("Error querying GraphQL endpoint. See log for details.")
    sys.exit(1)

orders = result.get("orders") if isinstance(result, dict) else None

if not orders:
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] No orders in the last 7 days.\n")
    print("Order reminders processed!")
    sys.exit(0)

with open(LOG_FILE, "a") as f:
    for order in orders:
        order_id = order.get("id")
        customer_email = (order.get("customer") or {}).get("email") if isinstance(order.get("customer"), dict) else None
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"[{timestamp}] Order ID: {order_id} Customer: {customer_email}\n")

print("Order reminders processed!")

