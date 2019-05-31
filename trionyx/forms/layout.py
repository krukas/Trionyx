"""
trionyx.forms.layout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from crispy_forms.layout import *  # noqa F403
from crispy_forms.bootstrap import *  # noqa F403

from trionyx.utils import (
    get_current_locale,
    get_datetime_input_format,
    datetime_format_to_django_template,
    datetime_format_to_momentjs
)


class DateTimePicker(Field):
    """DatetimePicker field renderer"""

    template = 'trionyx/forms/datetimepicker.html'

    glyphicon = 'glyphicon-calendar'

    locale = False
    """Locale of datetime picker default is active locale"""

    format = False
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
