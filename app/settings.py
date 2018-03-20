import os

from trionyx.settings import *


INSTALLED_APPS += [

    # Trionyx test app
    'app.testblog',

    # Development apps
    'django_extensions',
]

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


SECRET_KEY = 'dev-key-very-secure'
DEBUG = True

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'development.sqlite3'),
    }
}

ALLOWED_HOSTS = []

