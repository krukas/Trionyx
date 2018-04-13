"""Base Project settings"""
import os

from trionyx.settings import *  # noqa F403 F401

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

INSTALLED_APPS += [ # noqa F405
    # Extra apps
]

ROOT_URLCONF = 'config.urls'

ALLOWED_HOSTS = []

# Celery beat schedule
from trionyx.utils import create_celerybeat_schedule  # noqa E402
CELERY_BEAT_SCHEDULE = create_celerybeat_schedule(INSTALLED_APPS)

# Local settings
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Instead of doing "from .local_settings import *", we use exec so that
# local_settings has full access to everything defined in this module.
# Also force into sys.modules so it's visible to Django's autoreload.
local_settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'local_settings.py')
if os.path.exists(local_settings_path):
    import sys
    import types

    module = types.ModuleType('config.local_settings')
    module.__file__ = local_settings_path
    sys.modules['config.local_settings'] = module
    exec(open(local_settings_path, "rb").read())

# TODO inlude dev_settings.py
