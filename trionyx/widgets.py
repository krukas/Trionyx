"""
trionyx.widgets
~~~~~~~~~~~~~~~

:copyright: 2019 by Maikel Martens
:license: GPLv3
"""
import json
from collections import defaultdict
from typing import Dict, List, ClassVar, Type, Optional

from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.http.request import HttpRequest
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.contenttypes.models import ContentType
from django.forms import Form
from trionyx.trionyx.models import AuditLogEntry
from trionyx.renderer import renderer
from trionyx.config import models_config
from trionyx.trionyx.forms import AuditlogWidgetForm, TotalSummaryWidgetForm, GraphWidgetForm
from trionyx.models import Sum, filter_queryset_with_user_filters, Count
from trionyx.utils import get_current_request
from trionyx import utils
from django.utils.translation import ugettext_lazy as _


widgets: Dict[str, 'BaseWidget'] = {}


class WidgetDataRegister:
    """Class where widget data can be registered"""

    def __init__(self):
        """Init"""
        self.widget_data = defaultdict(dict)

    def register(self, widget, data_code, data_name, permission=None, **options):
        """Add data to register"""
        def wrapper(data_function):
            self.widget_data[widget.code][data_code] = {
                'name': data_name,
                'permission': permission,
                'function': data_function,
                'options': options,
            }
            return data_function
        return wrapper

    def get_all_data(self, widget):
        """Get all data"""
        user = getattr(get_current_request(), 'user', False) if get_current_request() else None
        return {
            name: data
            for name, data in self.widget_data.get(widget.code, {}).items()
            if (
                user and data['permission'] and user.has_perm(data['permission'])
            ) or (not user or not data['permission'])
        }

    def get_data(self, widget, code):
        """Get data"""
        user = getattr(get_current_request(), 'user', False) if get_current_request() else None
        data = self.widget_data[widget.code].get(code)

        if user and data and data['permission']:
            return data if user.has_perm(data['permission']) else {}

        return data


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

    permission: ClassVar[Optional[str]] = None
    """Permission to use this widget"""

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

    fixed_width: Optional[int] = None
    """Set a fixed width for widget"""

    fixed_height: Optional[int] = None
    """Set a fixed height for widget"""

    is_resizable: Optional[bool] = None
    """Is widget resizable"""

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

    @staticmethod
    def is_enabled() -> bool:
        """Determine if widget is enabled"""
        return True

    @classmethod
    def is_visible(cls, request) -> bool:
        """Check if widget is visible for given request"""
        user = getattr(request, 'user', False)
        visible = cls.is_enabled()

        if user and cls.permission:
            visible = visible and user.has_perm(cls.permission)

        return visible


class AuditlogWidget(BaseWidget):
    """Auditlog widget"""

    code = 'auditlog'
    name = _('Latest actions')
    description = _('Show the latest tracked actions done by users and the system')
    config_form_class = AuditlogWidgetForm
    default_height = 22

    @staticmethod
    def is_enabled():
        """Determine if AuditlogWidget is enabled"""
        return not settings.TX_DISABLE_AUDITLOG

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


# Total summary widget
# ---------------------------------------------------------------------------------------------------------------------
class TotalSummaryWidget(BaseWidget):
    """Total summary widget"""

    code = 'total_summary'
    name = _('Total summary')
    description = _('Show total for given field on given period')
    config_form_class = TotalSummaryWidgetForm
    fixed_height = 5

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


@register_data(TotalSummaryWidget, 'online_users_today', _('Unique users today'), icon='fa fa-user', color='purple')
def total_online_users(config):
    """Get total online users"""
    return get_user_model().objects.filter(
        last_online__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()


# Total summary widget
# ---------------------------------------------------------------------------------------------------------------------
class GraphWidget(BaseWidget):
    """Graph widget"""

    code = 'graph'
    name = _('Graph')
    description = _('Graph a sum of field or item count over given timeline')
    config_form_class = GraphWidgetForm
    default_height = 20

    colors = {
        'light-blue': {
            'fill': 'rgba(60, 141, 188, 0.2)',
            'stroke': 'rgba(60, 141, 188, 1)',
        },
        'aqua': {
            'fill': 'rgba(0, 192, 239, 0.2)',
            'stroke': 'rgba(0, 192, 239, 1)',
        },
        'green': {
            'fill': 'rgba(0, 166, 90, 0.2)',
            'stroke': 'rgba(0, 166, 90, 1)',
        },
        'yellow': {
            'fill': 'rgba(243, 156, 18, 0.2)',
            'stroke': 'rgba(243, 156, 18, 1)',
        },
        'red': {
            'fill': 'rgba(221, 75, 57, 0.2)',
            'stroke': 'rgba(221, 75, 57, 1)',
        },
        'gray': {
            'fill': 'rgba(210, 214, 222, 0.2)',
            'stroke': 'rgba(210, 214, 222, 1)',
        },
        'navy': {
            'fill': 'rgba(0, 31, 63, 0.2)',
            'stroke': 'rgba(0, 31, 63, 1)',
        },
        'teal': {
            'fill': 'rgba(57, 204, 204, 0.2)',
            'stroke': 'rgba(57, 204, 204, 1)',
        },
        'purple': {
            'fill': 'rgba(96, 92, 168, 0.2)',
            'stroke': 'rgba(96, 92, 168, 1)',
        },
        'orange': {
            'fill': 'rgba(255, 133, 27, 0.2)',
            'stroke': 'rgba(255, 133, 27, 1)',
        },
        'maroon': {
            'fill': 'rgba(216, 27, 96, 0.2)',
            'stroke': 'rgba(216, 27, 96, 1)',
        },
        'black': {
            'fill': 'rgba(17, 17, 17, 0.2)',
            'stroke': 'rgba(17, 17, 17, 1)',
        },
    }

    @classmethod
    def get_color(cls, color, color_type):
        """Get color"""
        color = color if color in cls.colors else 'light-blue'
        color_type = color_type if color_type in ['fill', 'stroke'] else 'stroke'

        return cls.colors[color][color_type]

    def get_data(self, request: HttpRequest, config: dict):
        """Get graph data"""
        if config.get('source', '__custom__') != '__custom__':
            func = widget_data.get_data(self, config.get('source')).get('function', lambda config: None)
            return func(config)

        try:
            ModelClass = ContentType.objects.get_for_id(config.get('model', -1)).model_class()
        except ContentType.DoesNotExist:
            return None

        if not ModelClass:
            return None

        from django.db.models.functions import ExtractMinute, ExtractHour, ExtractDay, ExtractWeek, ExtractMonth, ExtractYear
        interval_field = config.get('interval_field', 'created_at')
        query = ModelClass.objects.get_queryset().annotate(
            widget_minute=ExtractMinute(interval_field),
            widget_hour=ExtractHour(interval_field),
            widget_day=ExtractDay(interval_field),
            widget_week=ExtractWeek(interval_field),
            widget_month=ExtractMonth(interval_field),
            widget_year=ExtractYear(interval_field)
        )

        if config.get('filters'):
            query = filter_queryset_with_user_filters(query, json.loads(config['filters']))

        if config.get('interval_period') == 'minute':
            query = query.values('widget_minute', 'widget_hour', 'widget_day', 'widget_month', 'widget_year').order_by(
                'widget_year', 'widget_month', 'widget_day', 'widget_hour', 'widget_minute')
        elif config.get('interval_period') == 'hour':
            query = query.values('widget_hour', 'widget_day', 'widget_month', 'widget_year').order_by(
                'widget_year', 'widget_month', 'widget_day', 'widget_hour')
        elif config.get('interval_period') == 'day':
            query = query.values('widget_day', 'widget_month', 'widget_year').order_by(
                'widget_year', 'widget_month', 'widget_day')
        elif config.get('interval_period') == 'week':
            query = query.values('widget_week', 'widget_year').order_by(
                'widget_year', 'widget_week')
        elif config.get('interval_period') == 'month':
            query = query.values('widget_month', 'widget_year').order_by(
                'widget_year', 'widget_month')
        elif config.get('interval_period') == 'year':
            query = query.values('widget_year').order_by('widget_year')

        query = query.annotate(widget_count=Count('id'))

        model_config = models_config.get_config(ModelClass)
        only_count = config.get('field', '__count__') == '__count__'
        if only_count:
            label = model_config.get_verbose_name() + ' ' + str(_('Count'))
        else:
            query = query.annotate(widget_value=Sum(config['field']))
            label = _('Sum of {objects} {field}'.format(
                objects=model_config.get_verbose_name_plural(),
                field=model_config.get_field(config['field']).verbose_name
            ))

        query = query[:30]

        def row_to_date(row):
            """Based on row generate a date"""
            import datetime

            if config.get('interval_period') == 'week':
                return datetime.datetime.strptime('{}-W{}-1'.format(
                    row.get('widget_year'),
                    row.get('widget_week', 1) - 1,
                ), "%Y-W%W-%w").strftime('%Y-%m-%d %H:%M:%S')

            return datetime.datetime(
                year=row.get('widget_year'),
                month=row.get('widget_month', 1),
                day=row.get('widget_day', 1),
                hour=row.get('widget_hour', 0),
                minute=row.get('widget_minute', 0)
            ).strftime('%Y-%m-%d %H:%M:%S')

        datasets = []
        y_axes = [{
            'id': 'y-axis-2',
            'type': 'linear',
            'position': 'right' if not only_count else 'left',
            'gridLines': {
                'drawOnChartArea': False,
            },
            'ticks': {
                'suggestedMax': float(max([row['widget_count'] for row in query])) * (1.5 if not only_count else 1.10),
                'suggestedMin': 0,
            }
        }]
        if not only_count:
            field_renderer = renderer.renderers.get(type(model_config.get_field(config['field'])), lambda x: str(x))
            datasets.append({
                'label': label,
                'backgroundColor': self.get_color(config.get('color'), 'fill'),
                'borderColor': self.get_color(config.get('color'), 'stroke'),
                'pointBorderColor': self.get_color(config.get('color'), 'stroke'),
                'pointBackgroundColor': self.get_color(config.get('color'), 'stroke'),
                'fill': True,
                'pointRadius': 4,
                'data': [{
                    'x': row_to_date(row),
                    'y': row.get('widget_value'),
                    'label': field_renderer(row.get('widget_value')),
                } for row in query],
                'yAxisID': 'y-axis-1',
            })
            y_axes.append({
                'id': 'y-axis-1',
                'type': 'linear',
                'position': 'left',
                'gridLines': {
                    'drawOnChartArea': False,
                },
                'ticks': {
                    'suggestedMax': float(max([row['widget_value'] for row in query])) * 1.10,
                    'suggestedMin': 0,
                }
            })

        datasets.append({
            'label': str(_('Number of {objects}')).format(objects=model_config.get_verbose_name_plural()),
            'backgroundColor': self.get_color(config.get('color'), 'fill') if only_count else 'rgba(211, 211, 211, 0.2)',
            'borderColor': self.get_color(config.get('color'), 'stroke') if only_count else 'rgba(211, 211, 211, 1)',
            'pointBorderColor': self.get_color(config.get('color'), 'stroke') if only_count else 'rgba(211, 211, 211, 1)',
            'pointBackgroundColor': self.get_color(config.get('color'), 'stroke') if only_count else 'rgba(211, 211, 211, 1)',
            'fill': True,
            'pointRadius': 4,
            'data': [row.get('widget_count') for row in query],
            'yAxisID': 'y-axis-2',
        })

        return {
            'scales': {
                'xAxes': [{
                    'type': 'time',
                    'autoSkip': True,
                    'distribution': 'linear',
                    'time': {
                        'unit': config.get('interval_period', 'day'),
                        'stepSize': 1,
                        'tooltipFormat': utils.datetime_format_to_momentjs(utils.get_datetime_input_format(
                            date_only=config.get('interval_period') not in ['minute', 'hour']
                        ))
                    },
                }],
                'yAxes': y_axes,
            },
            'data': {
                'labels': [row_to_date(row) for row in query],
                'datasets': datasets,
            }
        }
