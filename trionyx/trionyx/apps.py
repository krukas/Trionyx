"""
trionyx.trionyx.apps
~~~~~~~~~~~~~~~~~~~~

Core apps package containing Appconfig

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from importlib import import_module

from django.apps import AppConfig
from django.apps import apps

from trionyx.config import models_config
from trionyx.navigation import app_menu, tabs
from trionyx.trionyx.search import auto_register_search_models


class BaseConfig(AppConfig):
    """Base app config"""

    def get_model_config(self, model):
        """Get model config for given model"""
        return models_config.get_config(model)


class Config(BaseConfig):
    """Trionyx core config app"""

    name = 'trionyx.trionyx'
    verbose_name = 'Trionyx'

    no_menu = True

    def ready(self):
        """Auto load Trionyx"""
        models_config.auto_load_configs()

        self.auto_load_app_modules(['layouts', 'signals'])

        app_menu.auto_load_model_menu()

        auto_register_search_models()
        tabs.auto_generate_missing_tabs()

    def auto_load_app_modules(self, modules):
        """Auto load app modules"""
        for app in apps.get_app_configs():
            for module in modules:
                try:
                    import_module('{}.{}'.format(app.module.__package__, module))
                except ImportError:
                    pass
