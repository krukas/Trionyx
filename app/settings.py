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

MIDDLEWARE = ('debug_toolbar.middleware.DebugToolbarMiddleware',) + MIDDLEWARE

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

LOGGING = {
	'version': 1,
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
		'apps': {
			'level': 'DEBUG',
			'handlers': ['console'],
		},
        'trionyx': {
			'level': 'DEBUG',
			'handlers': ['console'],
		},
        'django_jsend': {
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