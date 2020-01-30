"""Dev project settings"""
from .base import *  # noqa: F401,F403


INSTALLED_APPS += (
    'debug_toolbar',
    'django_extensions',
)

LOGIN_EXEMPT_URLS += (
    '__debug__',
)

MIDDLEWARE += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)


COMPRESS_ENABLED = False

DATABASES = {
    "default": {
        # Ends with "postgresql", "mysql", "sqlite3" or "oracle".
        "ENGINE": "django.db.backends.sqlite3",
        # DB name or path to database file if using sqlite3.
        "NAME": os.path.join(BASE_DIR, 'dev.sqlite3'),  # noqa F821
        # Not used with sqlite3.
        "USER": "",
        # Not used with sqlite3.
        "PASSWORD": "",
        # Set to empty string for localhost. Not used with sqlite3.
        "HOST": "",
        # Set to empty string for default. Not used with sqlite3.
        "PORT": "",
    }
}

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
