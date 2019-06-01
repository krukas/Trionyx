"""Dev project settings"""
from .base import *  # noqa: F401,F403

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
