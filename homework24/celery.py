import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homework24.settings')

app = Celery('homework24')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()