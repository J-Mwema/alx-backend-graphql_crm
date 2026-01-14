# CRM Celery & Beat Setup

This document explains how to set up the weekly CRM report using Celery and Celery Beat.

1. Install dependencies

```bash
pip install -r requirements.txt
```

2. Apply migrations (for django-celery-beat)

```bash
python manage.py migrate
```

3. Start Redis (default broker)

```bash
# Example using system service
sudo service redis-server start
# or using redis-server directly
redis-server &
```

4. Start a Celery worker

```bash
celery -A crm worker -l info
```

5. Start Celery Beat

```bash
celery -A crm beat -l info
```

6. Verify logs

The weekly report is logged to `/tmp/crm_report_log.txt` with a line like:

```
2026-01-13 06:00:00 - Report: X customers, Y orders, Z revenue
```
