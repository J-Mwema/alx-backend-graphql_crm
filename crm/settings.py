# Minimal settings for the CRM app relevant to cron jobs

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # django-crontab integration
    'django_crontab',
    # django-celery-beat for scheduled Celery tasks
    'django_celery_beat',
    # local app
    'crm',
]

# Configure django-crontab to run the heartbeat every 5 minutes and low-stock job every 12 hours
CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
    ('0 */12 * * *', 'crm.cron.update_low_stock'),
]

# Celery beat schedule for generating weekly CRM report (every Monday at 06:00)
from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
    },
}
