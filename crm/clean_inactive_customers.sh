#!/bin/bash

# Script to delete inactive customers (no orders since 1 year ago)
# and log the number of deleted customers.

LOG_FILE="/tmp/customer_cleanup_log.txt"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Run the Django command inside manage.py shell
DELETED_COUNT=$(python3 manage.py shell <<EOF
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer

one_year_ago = timezone.now() - timedelta(days=365)
deleted_count, _ = Customer.objects.filter(orders__isnull=True, created_at__lt=one_year_ago).delete()
print(deleted_count)
EOF
)

# Append results to the log file
echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers" >> "$LOG_FILE"

