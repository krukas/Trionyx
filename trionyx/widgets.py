"""
trionyx.widgets
~~~~~~~~~~~~~~~

:copyright: 2019 by Maikel Martens
:license: GPLv3
"""
import json
from collections import defaultdict
from typing import Dict, List, ClassVar, Type, Optional

from django.utils import timezone
from django.http.request import HttpRequest
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.contenttypes.models import ContentType
from django.forms import Form
from trionyx.trionyx.models import AuditLogEntry
from trionyx.renderer import renderer
from trionyx.config import models_config
from trionyx.trionyx.forms import AuditlogWidgetForm, TotalSummaryWidgetForm
from trionyx.models import Sum, filter_queryset_with_user_filters
from django.utils.translation import ugettext_lazy as _


widgets: Dict[str, 'BaseWidget'] = {}


class WidgetDataRegister:
    """Class where widget data can be registered"""

    def __init__(self):
        """Init"""
        self.widget_data = defaultdict(dict)

    def register(self, widget, data_code, data_name, **options):
        """Add data to register"""
        def wrapper(data_function):
            self.widget_data[widget.code][data_code] = {
                'name': data_name,
                'function': data_function,
                'options': options,
            }
            return data_function
        return wrapper

    def get_all_data(self, widget):
        """Get all data"""
        return self.widget_data.get(widget.code, None)

    def get_data(self, widget, code):
        """Get data"""
        return self.widget_data[widget.code].get(code)


widget_data = WidgetDataRegister()
register_data = widget_data.register


class MetaClass(type):
    """MetaClass for widget"""

    def __new__(cls, clsname, bases, attrs):
        """Auto register new widget cass"""
        newclass = super().__new__(cls, clsname, bases, attrs)
        if clsname != 'BaseWidget':
            widgets[newclass.code] = newclass
        return newclass


class BaseWidget(metaclass=MetaClass):
    """
    Base widget to extend for creating custom widgets.
    Custom widgets are created in `widgets.py` in root of app folder.

    **Example of random widget:**

    .. code-block:: python

        # <app dir>/widgets.py
        RandomWidget(BaseWidget):
            code = 'random'
            name = 'Random widget'
            description = 'Shows random string'

            def get_data(self, request, config):
                return utils.random_string(16)


    .. code-block:: html

        <!-- template path: widgets/random.html -->
        <script type="text/x-template" id="widget-random-template">
            <div :class="widgetClass">
                <div class="box-header with-border">
                    <!-- Get title from config, your form fields are also available in the config -->
                    <h3 class="box-title">[[widget.config.title]]</h3>
                </div>
                <!-- /.box-header -->
                <div class="box-body">
                    <!-- vue data property will be filled with the get_data results method --->
                    [[data]]
                </div>
              </div>
        </script>


        <script>
            <!-- The component must be called `widget-<code>` -->
            Vue.component('widget-random', {
                mixins: [TxWidgetMixin],
                template: '#widget-random-template',
            });
        </script>

    """

    code: ClassVar[str]
    """Code for widget"""

    name: ClassVar[str] = ''
    """Name for widget is also used as default title"""

    description: ClassVar[str] = ''
    """Short description on what the widget does"""

    config_form_class: ClassVar[Optional[Type[Form]]] = None
    """Form class used to change the widget. The form cleaned_data is used as the config"""

    default_width: ClassVar[int] = 4
    """Default width of widget, is based on grid system with max 12 columns"""

    default_height: ClassVar[int] = 20
    """Default height of widget, each step is 10px"""

    @property
    def template(self) -> str:
        """Template path `widgets/{code}.html` overwrite to set custom path"""
        return 'widgets/{code}.html'.format(code=self.code)

    @property
    def image(self) -> str:
        """Image path `img/widgets/{code}.jpg` overwrite to set custom path"""
        return 'img/widgets/{code}.jpg'.format(code=self.code)

    def get_data(self, request: HttpRequest, config: dict):
        """Get data for widget, function needs te be overwritten on widget implementation"""
        return None

    @property
    def config_fields(self) -> List[str]:
        """Get the config field names"""
        if not self.config_form_class:
            return []

        fields = list(self.config_form_class().base_fields)  # type: ignore

        for field in list(self.config_form_class().declared_fields):  # type: ignore
            if field not in fields:
                fields.append(field)
        return fields


class AuditlogWidget(BaseWidget):
    """Auditlog widget"""

    code = 'auditlog'
    name = _('Latest actions')
    description = _('Show the latest tracked actions done by users and the system')
    config_form_class = AuditlogWidgetForm
    default_height = 22

    def get_data(self, request: HttpRequest, config: dict) -> List[dict]:
        """Get data for widget"""
        content_type_ids = [
            content_type.id for model, content_type
            in ContentType.objects.get_for_models(*[
                config.model for config in models_config.get_all_configs(False)
                if request.user.has_perm('{app_label}.view_{model_name}'.format(
                    app_label=config.app_label,
                    model_name=config.model_name,
                ).lower())
            ]).items()]

        logs = AuditLogEntry.objects.filter(content_type__in=content_type_ids).prefetch_related('user')
        show = config.get('show', 'all')
        if show != 'all':
            logs = logs.filter(user__isnull=show == 'system')

        return [
            {
                'user_full_name': log.user.get_full_name() if log.user else _('System'),
                'user_avatar': log.user.avatar.url if log.user and log.user.avatar else static('img/avatar.png'),
                'action': renderer.render_field(log, 'action'),
                'object': '({}) {}'.format(
                    str(log.content_type.model_class()._meta.verbose_name).capitalize(),  # type: ignore
                    log.object_verbose_name),
                'object_url': log.content_object.get_absolute_url() if log.content_object else '',
                'created_at': renderer.render_field(log, 'created_at'),

            } for log in logs.order_by('-created_at')[:6]
        ]


class TotalSummaryWidget(BaseWidget):
    """Total summary widget"""

    code = 'total_summary'
    name = _('Total summary')
    description = _('Show total for given field on given period')
    config_form_class = TotalSummaryWidgetForm
    default_height = 5

    def get_data(self, request: HttpRequest, config: dict) -> str:
        """Get data"""
        if config.get('source', '__custom__') != '__custom__':
            func = widget_data.get_data(self, config.get('source')).get('function', lambda config: '-')
            return func(config)

        try:
            ModelClass = ContentType.objects.get_for_id(config.get('model', -1)).model_class()
        except ContentType.DoesNotExist:
            return '-'

        if not ModelClass:
            return ''

        query = ModelClass.objects.get_queryset()

        if config.get('filters'):
            query = filter_queryset_with_user_filters(query, json.loads(config['filters']))

        if config.get('period', 'all') != 'all':
            today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(**{
                'year': {
                    '{}__gte'.format(config['period_field']): today.replace(month=1, day=1)
                },
                'month': {
                    '{}__gte'.format(config['period_field']): today.replace(day=1)
                },
                'week': {
                    '{}__gte'.format(config['period_field']): today - timezone.timedelta(today.weekday())
                },
                'day': {
                    '{}__gte'.format(config['period_field']): today
                },
                '365days': {
                    '{}__gte'.format(config['period_field']): today - timezone.timedelta(days=365)
                },
                '30days': {
                    '{}__gte'.format(config['period_field']): today - timezone.timedelta(days=30)
                },
                '7days': {
                    '{}__gte'.format(config['period_field']): today - timezone.timedelta(days=7)
                },
            }.get(config['period'], {}))

        if config.get('field', '__count__') == '__count__':
            return renderer.render_value(query.count())
        else:
            result = query.aggregate(sum=Sum(config['field']))
            return renderer.render_field(ModelClass(**{config['field']: result['sum']}), config['field'])


@register_data(TotalSummaryWidget, 'online_users', _('Unique users today'), icon='fa fa-user', color='purple')
def total_online_users(config):
    """Get total online users"""
    from trionyx.trionyx.models import User
    return User.objects.filter(
        last_online__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()
