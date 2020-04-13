"""
trionyx.forms.layout
~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from crispy_forms.layout import TEMPLATE_PACK, Field, LayoutObject, Div  # Imports to satisfy MyPy
from crispy_forms.layout import *  # noqa F403
from crispy_forms.bootstrap import *  # noqa F403
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from trionyx import utils
from trionyx.config import models_config

from trionyx.utils import (
    get_current_locale,
    get_datetime_input_format,
    datetime_format_to_django_template,
    datetime_format_to_momentjs
)


class HtmlTemplate:
    """HTML template renderer"""

    def __init__(self, template, context=None):
        """Init layout object"""
        self.template = template
        self.context = context if context else {}

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        """Render template"""
        return render_to_string(self.template, {
            **context.flatten(),
            **self.context,
        })


class Depend(Div):
    """
    Depend layout only shows when all given form field dependencies match.

    Dependencies are given as list of tuples where first value is field name and second a regex value it should match.

    [
        ('language', r'(nl|be)')
    ]
    """

    template = 'trionyx/forms/depend.html'

    def __init__(self, dependencies, *args, **kwargs):
        """Init"""
        super().__init__(*args, **kwargs)
        self.dependencies = dependencies
        self.css_id = 'depend-' + utils.random_string(8)


class DateTimePicker(Field):
    """DatetimePicker field renderer"""

    template = 'trionyx/forms/datetimepicker.html'

    glyphicon = 'glyphicon-calendar'

    locale = False
    """Locale of datetime picker default is active locale"""

    format = ''
    """Date format, use python format: %Y-%m-%d %H:%M:%S"""

    day_view_header_format = 'MMMM YYYY'
    """Changes the heading of the datepicker when in "days" view."""

    stepping = 5
    """Number of minutes the up/down arrow's will move the minutes value in the time picker"""

    min_date = False
    """Prevents date/time selections before this date."""

    max_date = False
    """Prevents date/time selections after this date."""

    use_current = True
    """On show, will set the picker to the current date/time"""

    default_date = False
    """Sets the picker default date/time. Overrides useCurrent"""

    side_by_side = True
    """Shows the picker side by side when using the time and date together."""

    view_mode = 'days'
    """The default view to display when the picker is shown: 'decades','years','months','days'"""

    toolbar_placement = 'bottom'
    """Changes the placement of the icon toolbar: 'default', 'top', 'bottom'"""

    show_today_button = True
    """Show the "Today" button in the icon toolbar. Clicking the "Today" button will set the calendar view and set the date to now."""

    show_clear = True
    """Show the "Clear" button in the icon toolbar. Clicking the "Clear" button will set the calendar to null."""

    show_close = False
    """Show the "Close" button in the icon toolbar."""

    valid_options = [
        'locale',
        'format',
        'day_view_header_format',
        'stepping',
        'min_date',
        'max_date',
        'use_current',
        'default_date',
        'side_by_side',
        'view_mode',
        'toolbar_placement',
        'show_today_button',
        'show_clear',
        'show_close'
    ]

    def __init__(self, field, **kwargs):
        """Init DateTimePicker"""
        if not self.format:
            self.format = get_datetime_input_format()
        if 'format' in kwargs:
            self.format = kwargs.get('format')

        if not self.locale:
            self.locale = get_current_locale()

        for key in self.valid_options:
            value = kwargs.pop(key, getattr(self, key))
            if isinstance(value, bool):
                value = str(value).lower()
            kwargs['data-{}'.format(key)] = str(value if key != 'format' else datetime_format_to_momentjs(value))

        # Disable autocomplete default
        if 'autocomplete' not in kwargs:
            kwargs['autocomplete'] = 'off'

        kwargs['css_class'] = '{} datetimepicker datetimeinput form-control'.format(kwargs.get('css_class', '')).strip()
        super().__init__(field, **kwargs)

    def render(self, *args, **kwargs):
        """Render field"""
        extra_context = kwargs.get('extra_context', {})
        extra_context['glyphicon'] = self.glyphicon
        extra_context['input_format'] = datetime_format_to_django_template(self.format)
        kwargs['extra_context'] = extra_context
        return super().render(*args, **kwargs)


class TimePicker(DateTimePicker):
    """Timepicker field renderer"""

    format = '%H:%M'
    show_today_button = False
    glyphicon = 'glyphicon-time'


class InlineForm(LayoutObject):
    """Layout renderer for inline forms"""

    template = 'trionyx/forms/inlineform.html'

    def __init__(self, form_name, template=None):
        """Init Formset"""
        self.form_name = form_name
        if template:
            self.template = template

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        """Render form"""
        inline_form = form.get_inline_forms()[self.form_name]

        if hasattr(inline_form, 'forms'):
            config = models_config.get_config(inline_form.form._meta.model)
        else:
            config = models_config.get_config(inline_form._meta.model)

        return render_to_string(self.template, {
            'inline_form_prefix': self.form_name,
            'inline_form_verbose_name': config.get_verbose_name(),
            'inline_form': inline_form,
        }, utils.get_current_request())


class Filters:
    """Form Filter field"""

    def __init__(self, name, model=None, content_type_input_id=None):
        """Init Filter field, model or content_type_input_id must be supplied"""
        self.name = name
        self.model = model
        self.content_type_input_id = content_type_input_id

        if not model and not content_type_input_id:
            raise Exception('A model or content_type_input_id must be supplied')

    def render(self, form, form_style, context, **kwargs):
        """Render template"""
        value = form.data.get(self.name, form.initial.get(self.name, '[]'))
        if not value:
            value = '[]'

        return render_to_string('trionyx/forms/filters.html', {
            **context.flatten(),
            'uuid': utils.random_string(8),
            'name': self.name,
            'value': value,
            'content_type_input_id': self.content_type_input_id,
            'content_type_id': ContentType.objects.get_for_model(self.model).id if self.model else -1
        })
