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
