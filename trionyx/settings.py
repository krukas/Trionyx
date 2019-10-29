# Copyright 2019 by Maikel Martens
#
# License GPLv3

"""
Settings
========

All Trionyx base settings
"""
import json
import logging
import os
from pkg_resources import iter_entry_points

from django.core.exceptions import ImproperlyConfigured
from kombu import Queue, Exchange


def gettext_noop(s):
    """Return same string, Dummy function to find translatable strings with makemessages"""
    return s


try:
    with open(os.path.abspath(os.environ.get('TRIONYX_CONFIG', 'environment.json'))) as f:
        trionyx_config = json.loads(f.read())
except FileNotFoundError:
    raise ImproperlyConfigured(
        "Could not load Trionyx config file, is env variable TRIONYX_CONFIG correctly configuerd?")


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
    # Trionyx core app
    'trionyx.trionyx',

    # Add installed trionyx apps
    *[entry_point.module_name for entry_point in iter_entry_points(group='trionyx.app', name=None)],

    # Django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'rest_framework',
    'rest_framework.authtoken',
    'watson',
    'crispy_forms',
    'compressor',
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Etc/GMT'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en-us', gettext_noop('English')),
    ('nl', gettext_noop('Dutch')),
]

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
    'trionyx.trionyx.middleware.LocalizationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'trionyx.trionyx.middleware.LoginRequiredMiddleware',
    'trionyx.trionyx.middleware.GlobalRequestMiddleware',
    'trionyx.trionyx.middleware.LastLoginMiddleware',
)

# ==============================================================================
# Auth / security
# ==============================================================================
AUTH_USER_MODEL = 'trionyx.User'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

LOGIN_EXEMPT_URLS = [
    'static',
    'api',
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
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'trionyx.api.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'trionyx.api.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

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

TX_THEME_COLOR = 'purple'
"""The theme skin color (header). Aviable colors: blue, yellow, green, purple, red, black. All colors have a light version blue-light"""


def TX_DEFAULT_DASHBOARD():
    """Return default dashboard"""
    from django.contrib.contenttypes.models import ContentType
    from django.utils.translation import ugettext as _
    return [
        {
            "code": "auditlog",
            "config": {
                "title": _("Action history"),
                "color": "light-blue",
                "show": "all",
                "refresh": "0"
            },
            "x": 0,
            "y": 5,
            "w": 6,
            "h": 22,
        },
        {
            "code": "total_summary",
            "config": {
                "title": _("Unique users today"),
                "color": "purple",
                "model": ContentType.objects.get_by_natural_key('trionyx', 'user').id,
                "field": "__count__",
                "icon": "fa fa-user",
                "period": "day",
                "period_field": "last_online",
                "refresh": "15"
            },
            "x": 0,
            "y": 0,
            "w": 4,
            "h": 5,
        },
        {
            "code": "total_summary",
            "config": {
                "title": _("New users this week"),
                "color": "green",
                "refresh": "15",
                "icon": "fa fa-user-plus",
                "model": ContentType.objects.get_by_natural_key('trionyx', 'user').id,
                "field": "__count__",
                "period": "week",
                "period_field": "created_at"
            },
            "x": 4,
            "y": 0,
            "w": 4,
            "h": 5,
        },
        {
            "code": "total_summary",
            "config": {
                "title": _("User count"),
                "color": "yellow",
                "refresh": "0",
                "icon": "fa fa-users",
                "model": ContentType.objects.get_by_natural_key('trionyx', 'user').id,
                "field": "__count__",
                "period": "all",
                "period_field": ""
            },
            "x": 8,
            "y": 0,
            "w": 4,
            "h": 5,
        }
    ]


TX_MODEL_OVERWRITES = {}
"""
Config to overwrite models, its a dict where the key is the original `app_label.model_name` and value is the new one.

.. code-block:: python

    TX_MODEL_OVERWRITES = {
        'trionyx.User': 'local.User',
    }
"""

TX_MODEL_CONFIGS = {}
"""
Dict with configs for non Trionyx model, example:

.. code-block:: python

    TX_MODEL_CONFIGS = {
        'auth.group': {
            'list_default_fields': ['name'],
            'disable_search_index': False,
        }
    }
"""

TX_CORE_MODEL_CONFIGS = {
    'auth.group': {
        'list_default_fields': ['name'],
        'disable_search_index': False,
    },
    'watson.searchentry': {
        'hide_permissions': True,
    },
    'trionyx.userattribute': {
        'hide_permissions': True,
    },
    'trionyx.logentry': {
        'hide_permissions': True,
    },
    'trionyx.auditlogentry': {
        'hide_permissions': True,
    },
    'sessions.session': {
        'hide_permissions': True,
    },
    'contenttypes.contenttype': {
        'hide_permissions': True,
    },
    'authtoken.token': {
        'hide_permissions': True,
    },
    'auth.permission': {
        'hide_permissions': True,
    },
}

TX_DB_LOG_LEVEL = logging.WARNING
"""The DB log level for logging"""
