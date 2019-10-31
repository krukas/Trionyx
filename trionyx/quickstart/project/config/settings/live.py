"""Live project settings"""
from .base import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'error-file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'error.log'),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'apps': {
            'level': 'WARNING',
            'handlers': ['file', 'error-file'],
        },
        'trionyx': {
            'level': 'WARNING',
            'handlers': ['error-file'],
        },
        'django_jsend': {
            'level': 'ERROR',
            'handlers': ['error-file'],
        },
        'django': {
            'level': 'ERROR',
            'handlers': ['error-file'],
        },
    }
}
