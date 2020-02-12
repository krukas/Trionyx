"""Live project settings"""
from .base import *  # noqa: F401,F403
import os


LOG_DIR = get_env_var('LOG_DIR', BASE_DIR)
os.makedirs(LOG_DIR, exist_ok=True)


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
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'error.log'),
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'apps': {
            'level': 'WARNING',
            'handlers': ['error-file'],
        },
        'trionyx': {
            'level': 'WARNING',
            'handlers': ['error-file'],
        },
        'django': {
            'level': 'ERROR',
            'handlers': ['error-file'],
        },
    }
}
