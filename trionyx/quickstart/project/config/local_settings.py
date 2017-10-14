"""
Local project settings, DON't include in your code repository.

This file is exec'd from settings.py, so it has access to and can
modify all the variables in settings.py.
"""
import os

DEBUG = True

# Make these unique, and don't share it with anybody.
SECRET_KEY = "[[secret_key]]"

DATABASES = {
    "default": {
        # Ends with "postgresql_psycopg2", "mysql", "sqlite3" or "oracle".
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
