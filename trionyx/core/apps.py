"""
trionyx.core.apps
~~~~~~~~~~~~~~~~~

Core apps package containing Appconfig

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
from importlib import import_module

from django.apps import AppConfig
from django.apps import apps


class BaseConfig(AppConfig):
	pass

class Config(BaseConfig):
    """Django core config app"""

    name = 'trionyx.core'
    verbose_name = 'Core'

    def ready(self):
        for app in apps.get_app_configs():
            try:
                import_module('{}.{}'.format(app.module.__package__, 'layouts'))
            except ImportError:
                pass
