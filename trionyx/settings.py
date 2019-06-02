# Copyright 2019 by Maikel Martens
#
# License GPLv3

"""
Settings
========

All Trionyx base settings
"""
import os
import json

from kombu import Queue, Exchange
from django.core.exceptions import ImproperlyConfigured

try:
    with open(os.path.abspath(os.environ.get('TRIONYX_CONFIG', 'environment.json'))) as f:
        trionyx_config = json.loads(f.read())
except FileNotFoundError:
    raise ImproperlyConfigured("Could not load Trionyx config file, is env variable TRIONYX_CONFIG correctly configuerd?")


def get_env_var(setting, default=None, configs=trionyx_config):
    """
    Get environment variable from the environment json file

    Default environment file is `environment.json` in the root of project,
    Other file path can be set with the `TRIONYX_CONFIG` environment variable
    """
    try:
        return configs[setting]
    except KeyError:
        if default is not None:
            return default
        raise ImproperlyConfigured("ImproperlyConfigured: Set {} environment variable".format(setting))


DEBUG = get_env_var('DEBUG', False)
ALLOWED_HOSTS = get_env_var('ALLOWED_HOSTS', [])
SECRET_KEY = get_env_var('SECRET_KEY')

INSTALLED_APPS = [
    # Trionyx apps
    'trionyx.trionyx',

    # Django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'watson',
    'crispy_forms',
    'compressor',
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ==============================================================================
# Project URLS and media settings
# ==============================================================================
ROOT_URLCONF = 'trionyx.urls'

LOGIN_URL = 'trionyx:login'
LOGOUT_URL = 'trionyx:logout'
LOGIN_REDIRECT_URL = '/'

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

WSGI_APPLICATION = 'wsgi.application'

# ==============================================================================
# Middleware
# ==============================================================================
MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'trionyx.trionyx.middleware.LoginRequiredMiddleware',
)

# ==============================================================================
# Auth / security
# ==============================================================================
AUTH_USER_MODEL = 'trionyx.User'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

LOGIN_EXEMPT_URLS = [
    'static',
]
"""A list of urls that dont require a login"""

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==============================================================================
# Templates
# ==============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',

                'django.contrib.messages.context_processors.messages',
                'trionyx.trionyx.context_processors.trionyx',
            ],
        }
    },
]

CRISPY_TEMPLATE_PACK = 'bootstrap3'

# ==============================================================================
# Compressor
# ==============================================================================
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]

COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True

# ==============================================================================
# Cache backend
# ==============================================================================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache',
    }
}

CORS_ORIGIN_WHITELIST = [
    'localhost:8000',
]

# ==============================================================================
# Celery
# ==============================================================================
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'

CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_ENABLE_UTC = True

CELERY_QUEUES = (
    Queue('cron', Exchange('cron'), routing_key='cron'),
    Queue('low_prio', Exchange('low_prio'), routing_key='low_prio'),
    Queue('high_prio', Exchange('high_prio'), routing_key='high_prio'),
)
CELERY_TASK_DEFAULT_QUEUE = 'low_prio'

CELERY_TASK_SOFT_TIME_LIMIT = 3600
CELERY_TASK_TIME_LIMIT = 3900

# ==============================================================================
# Trionyx settings
# ==============================================================================
TX_APP_NAME = 'Trionyx'
"""Full application name"""

TX_LOGO_NAME_START = 'Tri'
"""The first characters of the name that are bold"""

TX_LOGO_NAME_END = 'onyx'
"""The rest of the characters"""

TX_LOGO_NAME_SMALL_START = 'T'
"""The first character or characters of the small logo that is bold"""

TX_LOGO_NAME_SMALL_END = 'X'
"""The last character or characters of the small logo that is normal"""

TX_THEME_COLOR = 'blue'
"""The theme skin color (header). Aviable colors: blue, yellow, green, purple, red, black. All colors have a light version blue-light"""

TX_MODEL_CONFIGS = {}
"""
Dict with configs for non Trionyx model, example:

.. code-block:: python

    TX_MODEL_CONFIGS = 'auth.group': {
        'list_default_fields': ['name'],
        'disable_search_index': False,
    }

"""

TX_CORE_MODEL_CONFIGS = {
    'auth.group': {
        'list_default_fields': ['name'],
        'disable_search_index': False,
    }
}
