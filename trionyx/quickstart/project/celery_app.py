"""Project Celery app"""
import os

from celery import Celery
from celery.signals import after_setup_logger
from trionyx.log import enable_db_logger

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create celery app
app = Celery('trionyx')

# Get celery config from django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    """Enable DB logger for celery"""
    enable_db_logger()
