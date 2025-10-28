#!/bin/bash

# Script to delete customers with no orders since a year ago
# and log the number of deleted customers with a timestamp.

LOG_FILE="/tmp/customer_cleanup_log.txt"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

DELETED_COUNT=$(python3 manage.py shell <<EOF
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer

one_year_ago = timezone.now() - timedelta(days=365)
deleted_count, _ = Customer.objects.filter(orders__isnull=True, created_at__lt=one_year_ago).delete()
print(deleted_count)
EOF
)

echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers" >> "$LOG_FILE"

