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

MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOCALE_PATHS = (
	os.path.join(BASE_DIR, 'trionyx', 'trionyx', 'locale'),
)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SECRET_KEY = 'dev-key-very-secure'
DEBUG = True
COMPRESS_ENABLED = False

TX_CHANGELOG_HASHTAG_URL = 'https://github.com/krukas/Trionyx/issues/{tag}'

# Database
DATABASES = get_env_var('DATABASES', {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'development.sqlite3'),
    }
})

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
   }
}

ALLOWED_HOSTS = []

WATSON_POSTGRES_SEARCH_CONFIG = get_watson_search_config(LANGUAGE_CODE)

# Celery beat schedule
from trionyx.utils import create_celerybeat_schedule
CELERY_BEAT_SCHEDULE = create_celerybeat_schedule(INSTALLED_APPS)

LOGGING = {
	'version': 1,
    'disable_existing_loggers': False,
	'formatters': {
		'color_console': {
			'()': 'colorlog.ColoredFormatter',
			'format': '%(log_color)s%(levelname)-8s [%(name)s:%(lineno)s]%(reset)s %(blue)s %(message)s',
			'datefmt': "%d/%b/%Y %H:%M:%S",
			'log_colors': {
				'DEBUG': 'cyan',
				'INFO': 'green',
				'WARNING': 'yellow',
				'ERROR': 'red',
				'CRITICAL': 'red',
			},
		},
	},
	'filters': {
		'require_debug_true': {
			'()': 'django.utils.log.RequireDebugTrue',
		}
	},
	'handlers': {
		'console': {
			'level': 'DEBUG',
			'filters': ['require_debug_true'],
			'class': 'logging.StreamHandler',
			'formatter': 'color_console',
		}
	},
	'loggers': {
		'app': {
			'level': 'DEBUG',
			'handlers': ['console'],
		},
        'trionyx': {
			'level': 'DEBUG',
			'handlers': ['console'],
		},
		# 'django.db.backends': {
		#     'level': 'DEBUG',
		#     'handlers': ['console'],
		# },
		'werkzeug': {
			'handlers': ['console'],
			'level': 'DEBUG',
			'propagate': True,
		},
	}
}