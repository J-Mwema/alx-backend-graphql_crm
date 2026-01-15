#!/bin/bash



# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

# Run Django shell command to delete inactive customers
python manage.py shell << 'EOF'
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order

# Calculate date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders in the last year
inactive_customers = []
for customer in Customer.objects.all():
	if not Order.objects.filter(customer=customer, order_date_gte=one_year_ago).exists():
		inactive_customers.append(customer)


# Delete inactive customers
count = len(inactive_customers)
for customer in inactive_customers:
	customer.delete()

# Log the result
log_message = f"[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] Deleted {count} inactive customers\n"
with open('/tmp/customer_cleanup_log.txt', 'a') as f:
	f.write(log_message)
print(f"Deleted {count} inactive customers")
EOF
