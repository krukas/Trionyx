import os

from trionyx.settings import *

INTERNAL_IPS = ('127.0.0.1','::1', '0.0.0.0')

INSTALLED_APPS += [

    # Trionyx test app
    'app.testblog',

    # Development apps
    'django_extensions',
    'debug_toolbar',
]

MIDDLEWARE_CLASSES = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE_CLASSES

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SECRET_KEY = 'dev-key-very-secure'
DEBUG = True
COMPRESS_ENABLED = False

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'development.sqlite3'),
    }
}

ALLOWED_HOSTS = []

# Celery beat schedule
from trionyx.utils import create_celerybeat_schedule
CELERY_BEAT_SCHEDULE = create_celerybeat_schedule(INSTALLED_APPS)