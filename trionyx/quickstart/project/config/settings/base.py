"""Base Project settings"""
from trionyx.settings import *  # noqa F403 F401


TX_APP_NAME = '[[app_name]]'
TX_LOGO_NAME_START = '[[logo_name_start]]'
TX_LOGO_NAME_END = '[[logo_name_end]]'
TX_LOGO_NAME_SMALL_START = '[[logo_name_small_start]]'
TX_LOGO_NAME_SMALL_END = '[[logo_name_small_end]]'

TX_COMPANY_NAME = '[[app_name]]'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

INSTALLED_APPS += [ # noqa F405
    # Extra apps
]

ROOT_URLCONF = 'config.urls'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

WATSON_POSTGRES_SEARCH_CONFIG = get_watson_search_config(LANGUAGE_CODE)

# Celery beat schedule
from trionyx.utils import create_celerybeat_schedule  # noqa E402
CELERY_BEAT_SCHEDULE = create_celerybeat_schedule(INSTALLED_APPS)
