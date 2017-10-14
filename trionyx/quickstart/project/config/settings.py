"""Base Project settings"""
import os

from trionyx.settings import *  # noqa F403 F401

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_APPS = [
    # Django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',

    # Rest framework apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    # Trionyx apps
    'trionyx.core',
]

ROOT_URLCONF = 'config.urls'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

ALLOWED_HOSTS = []

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
