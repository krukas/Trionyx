"""
trionyx.trionyx.apps
~~~~~~~~~~~~~~~~~~~~

Core apps package containing Appconfig

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from importlib import import_module
from typing import Optional, Union, List, Type

from django.apps import AppConfig
from django.apps import apps
from django.utils import timezone
from django.db.models import Model

from trionyx.config import models_config, ModelConfig
from trionyx.menu import app_menu
from trionyx.trionyx.search import auto_register_search_models
from trionyx.log import enable_db_logger
from django.utils.translation import ugettext_lazy as _
from django.contrib.staticfiles.templatetags.staticfiles import static

from .renderers import render_level, render_progress, render_status


class BaseConfig(AppConfig):
    """Base app config"""

    def get_model_config(self, model: Union[str, Type[Model]]) -> Optional[ModelConfig]:
        """Get model config for given model"""
        return models_config.get_config(model)


class Config(BaseConfig):
    """Trionyx core config app"""

    name = 'trionyx.trionyx'
    verbose_name = _('System')

    no_menu = True

    def ready(self):
        """Auto load Trionyx"""
        enable_db_logger()

        models_config.auto_load_configs()

        from trionyx import widgets  # noqa F401
        self.auto_load_app_modules(['layouts', 'signals', 'forms', 'widgets'])

        app_menu.auto_load_model_menu()

        auto_register_search_models()

        from trionyx.views import tabs
        tabs.auto_generate_missing_tabs()

        from trionyx.trionyx.auditlog import init_auditlog
        init_auditlog()

        # Add admin menu items
        from trionyx.urls import model_url
        app_menu.add_item('dashboard', _('Dashboard'), url='/', icon='fa fa-dashboard', order=1)
        app_menu.add_item('admin', _('Admin'), icon='fa fa-cogs', order=9000, permission='is_superuser')
        app_menu.add_item('admin/users', _('Users'), url=model_url('trionyx.user', 'list'), order=9010, permission='is_superuser')
        app_menu.add_item(
            'admin/groups', _('Permission groups'), url=model_url('auth.group', 'list'), order=9010, permission='is_superuser')
        app_menu.add_item('admin/logs', _('Logs'), url=model_url('trionyx.log', 'list'), order=9090, permission='is_superuser')

        # Add User renderer
        from trionyx.models import get_class
        from trionyx.renderer import renderer
        renderer.register(
            get_class('trionyx.User'),
            lambda value, **options: """<img src="{url}" class="avatar-sm" title="{user}">""".format(
                url=value.avatar.url if value.avatar else static('img/avatar.png'),
                user=str(value)
            ))

    def auto_load_app_modules(self, modules: List[str]):
        """Auto load app modules"""
        for app in apps.get_app_configs():
            for module in modules:
                try:
                    import_module('{}.{}'.format(getattr(app.module, '__package__'), module))
                except ImportError as e:
                    if str(e) != "No module named '{}.{}'".format(getattr(app.module, '__package__'), module):
                        raise e

    class User(ModelConfig):
        """User config"""

        list_default_fields = ['created_at', 'email', 'first_name', 'last_name', 'is_active', 'is_superuser']
        auditlog_ignore_fields = ['last_online', 'last_login']
        verbose_name = '{email}'

    class Log(ModelConfig):
        """Log config"""

        verbose_name = '{message}'

        disable_add = True
        disable_change = True
        disable_delete = True

        global_search = False
        auditlog_disable = True
        api_disable = True

        list_default_fields = ['level', 'last_event', 'log_count', 'message']
        list_default_sort = '-last_event'
        list_fields = [
            {
                'field': 'level',
                'label': _('Level'),
                'renderer': render_level
            }
        ]

    class AuditLogEntry(ModelConfig):
        """AuditlogEntry config"""

        disable_search_index = True

        disable_add = True
        disable_change = True
        disable_delete = True

        auditlog_disable = True
        api_disable = True

    class Task(ModelConfig):
        """Task config"""

        verbose_name = '{description}'

        list_default_fields = ['created_at', 'description', 'user', 'status', 'progress', 'started_at', 'execution_time', 'result']

        list_fields = [
            {
                'field': 'status',
                'renderer': render_status,
            },
            {
                'field': 'progress',
                'renderer': render_progress,
            },
            {
                'field': 'execution_time',
                'renderer': lambda obj, *args, **options: str(timezone.timedelta(seconds=obj.execution_time)),
            },
        ]

        disable_search_index = True
        menu_exclude = True

        disable_add = True
        disable_change = True
        disable_delete = True

        auditlog_disable = True
        api_disable = True
