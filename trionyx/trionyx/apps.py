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
from trionyx.menu import app_menu
from trionyx.trionyx.search import auto_register_search_models
from trionyx.log import enable_db_logger

from .renderers import render_level


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
        enable_db_logger()

        models_config.auto_load_configs()

        self.auto_load_app_modules(['layouts', 'signals', 'forms'])

        app_menu.auto_load_model_menu()

        auto_register_search_models()

        from trionyx.views import tabs
        tabs.auto_generate_missing_tabs()

        from trionyx.trionyx.auditlog import init_auditlog
        init_auditlog()

        # Add admin menu items
        from trionyx.urls import model_url
        app_menu.add_item('admin', 'Admin', icon='fa fa-cogs', order=9000, permission='is_superuser')
        app_menu.add_item('admin/users', 'Users', url=model_url('trionyx.user', 'list'), order=9010, permission='is_superuser')
        app_menu.add_item('admin/groups', 'Permission groups', url=model_url('auth.group', 'list'), order=9010, permission='is_superuser')
        app_menu.add_item('admin/logs', 'Logs', url=model_url('trionyx.log', 'list'), order=9090, permission='is_superuser')

    def auto_load_app_modules(self, modules):
        """Auto load app modules"""
        for app in apps.get_app_configs():
            for module in modules:
                try:
                    import_module('{}.{}'.format(app.module.__package__, module))
                except ImportError:
                    pass

    class User:
        """User config"""

        list_default_fields = ['created_at', 'email', 'first_name', 'last_name', 'is_active', 'is_superuser']
        auditlog_ignore_fields = ['last_online', 'last_login']

    class Log:
        """Log config"""

        verbose_name = '{message}'

        disable_add = True
        disable_change = True
        disable_delete = True

        global_search = False
        auditlog_disable = True
        api_disable = True

        list_default_fields = ['message', 'level', 'last_event', 'log_count']
        list_default_sort = '-last_event'
        list_fields = [
            {
                'field': 'level',
                'label': 'Level',
                'renderer': render_level
            }
        ]

    class AuditLogEntry:
        """AuditlogEntry config"""

        disable_search_index = True

        disable_add = True
        disable_change = True
        disable_delete = True

        auditlog_disable = True
        api_disable = True
