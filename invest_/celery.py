import os  
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'invest_.settings')
celery_app = Celery('invest_')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')  
celery_app.autodiscover_tasks()

# celery -A invest_  worker -l inf
