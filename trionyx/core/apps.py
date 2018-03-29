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

from trionyx.config import models_config
from trionyx.navigation import Menu


class BaseConfig(AppConfig):
    def get_model_config(self):
        pass

class Config(BaseConfig):
    """Django core config app"""

    name = 'trionyx.core'
    verbose_name = 'Core'

    no_menu = True

    def ready(self):
        models_config.auto_load_configs()

        for app in apps.get_app_configs():
            try:
                import_module('{}.{}'.format(app.module.__package__, 'layouts'))
            except ImportError:
                pass

        Menu.auto_load_model_menu()
