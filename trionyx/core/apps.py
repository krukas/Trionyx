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
from trionyx.core.search import auto_register_search_models


class BaseConfig(AppConfig):
    """Base app config"""

    def get_model_config(self, model):
        """Get model config for given model"""
        return models_config.get_config(model)


class Config(BaseConfig):
    """Django core config app"""

    name = 'trionyx.core'
    verbose_name = 'Core'

    no_menu = True

    def ready(self):
        """Auto load Trionyx"""
        models_config.auto_load_configs()

        for app in apps.get_app_configs():
            try:
                import_module('{}.{}'.format(app.module.__package__, 'layouts'))
            except ImportError:
                pass

        Menu.auto_load_model_menu()

        auto_register_search_models()
