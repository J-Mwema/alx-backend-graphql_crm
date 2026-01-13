#!/bin/bash

set -euo pipefail

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Project root is two levels up from crm/cron_jobs
PROJECT_DIR="$( cd "$SCRIPT_DIR/../.." && pwd )"

# Change to the project directory so that manage.py and Django settings are available
cd "$PROJECT_DIR"

# Use Django's manage.py shell to execute the cleanup logic within Django's environment.
# We run a small Python script that:
#  - computes the date 1 year ago,
#  - finds all Customer instances with NO related Order in the last year,
#  - deletes those customers, and
#  - logs the number deleted to /tmp/customer_cleanup_log.txt with a timestamp.
python manage.py shell << 'PY'
# Import utilities for timezone-aware datetimes
from django.utils import timezone
from datetime import timedelta
# Import the models we will operate on. Adjust these imports if your app or model names differ.
from crm.models import Customer, Order

# Compute cutoff datetime: any order must be newer than this to be considered "active"
one_year_ago = timezone.now() - timedelta(days=365)

# Track how many customers we delete for reporting/logging
count = 0
# Iterate through all customers (suitable for small datasets). For large datasets consider a queryset-based delete.
for customer in Customer.objects.all():
    # If the customer has no orders with created >= one_year_ago, consider them inactive
    if not Order.objects.filter(customer=customer, created__gte=one_year_ago).exists():
        # Deleting the Customer instance will also remove related dependent records depending on your model cascade settings
        customer.delete()
        count += 1

# Write a timestamped log entry to /tmp/customer_cleanup_log.txt for audit and debugging
log_message = f"[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] Deleted {count} inactive customers\n"
with open('/tmp/customer_cleanup_log.txt', 'a') as f:
    f.write(log_message)

# Print a short message so cron logs capture the outcome when it runs
print(f"Deleted {count} inactive customers")
PY
