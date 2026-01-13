#!/bin/bash

set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Project root is two levels up from crm/cron_jobs
PROJECT_DIR="$( cd "$SCRIPT_DIR/../.." && pwd )"

# Change to project directory
cd "$PROJECT_DIR"

# Run Django shell command to delete inactive customers
python manage.py shell << 'PY'
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order

one_year_ago = timezone.now() - timedelta(days=365)

count = 0
for customer in Customer.objects.all():
    # Check if customer has any orders in the past year
    if not Order.objects.filter(customer=customer, created__gte=one_year_ago).exists():
        customer.delete()
        count += 1

# Log the result with a timestamp
log_message = f"[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] Deleted {count} inactive customers\n"
with open('/tmp/customer_cleanup_log.txt', 'a') as f:
    f.write(log_message)

print(f"Deleted {count} inactive customers")
PY
