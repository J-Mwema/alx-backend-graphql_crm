"""Cron tasks for the `crm` app."""

from datetime import datetime

# Optional: use requests to verify the GraphQL endpoint
try:
    import requests
except Exception:
    requests = None

LOG_FILE = "/tmp/crm_heartbeat_log.txt"


def log_crm_heartbeat():
    """Append a heartbeat message to `LOG_FILE`.

    Format: DD/MM/YYYY-HH:MM:SS CRM is alive
    Optionally queries the GraphQL `hello` field to confirm responsiveness.
    """
    ts = datetime.utcnow().strftime('%d/%m/%Y-%H:%M:%S')
    msg = f"{ts} CRM is alive\n"
    with open(LOG_FILE, 'a') as f:
        f.write(msg)

    # Optionally attempt a small GraphQL hello query to verify the endpoint
    if requests:
        try:
            resp = requests.post('http://localhost:8000/graphql', json={'query': '{ hello }'}, timeout=5)
            if resp.ok:
                # write a short note that the GraphQL endpoint responded
                with open(LOG_FILE, 'a') as f:
                    f.write(f"{ts} GraphQL hello response: {resp.text}\n")
            else:
                with open(LOG_FILE, 'a') as f:
                    f.write(f"{ts} GraphQL hello non-OK response: {resp.status_code}\n")
        except Exception as exc:
            with open(LOG_FILE, 'a') as f:
                f.write(f"{ts} GraphQL hello check failed: {exc}\n")
