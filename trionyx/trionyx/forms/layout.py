"""
trionyx.trionyx.forms.layout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from django.utils import formats
from crispy_forms.layout import Field

from trionyx.utils import get_current_locale


class DateTimePicker(Field):
    """

    """

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
            self.format = formats.get_format_lazy('DATETIME_INPUT_FORMATS')[0]

        if not self.locale:
            self.locale = get_current_locale()

        for key in self.valid_options:
            value = kwargs.pop(key, getattr(self, key))
            if isinstance(value, bool):
                value = str(value).lower()
            kwargs['data-{}'.format(key)] = str(value if key != 'format' else self.convert_pyton_to_momentjs(value))

        # Disable autocomplete default
        if 'autocomplete' not in kwargs:
            kwargs['autocomplete'] = 'off'

        kwargs['css_class'] = '{} datetimepicker datetimeinput form-control'.format(kwargs.get('css_class', '')).strip()
        super().__init__(field, **kwargs)

    def render(self, *args, **kwargs):
        extra_context = kwargs.get('extra_context', {})
        extra_context['glyphicon'] = self.glyphicon
        extra_context['input_format'] = self.convert_python_to_django_template(self.format)
        kwargs['extra_context'] = extra_context
        return super().render(*args, **kwargs)

    def convert_pyton_to_momentjs(self, format):
        mapping = {
            '%a': 'ddd',
            '%A': 'dddd',
            '%w': 'd',
            '%d': 'DD',
            '%b': 'MMM',
            '%B': 'MMMM',
            '%m': 'MM',
            '%y': 'YY',
            '%Y': 'YYYY',
            '%H': 'HH',
            '%I': 'hh',
            '%p': 'A',
            '%M': 'mm',
            '%S': 'ss',
            '%f': 'SSS',
            '%z': 'ZZ',
            '%Z': 'z',
            '%j': 'DDDD',
            '%U': 'ww',
            '%W': 'ww',
            '%c': 'ddd MMM DD HH:mm:ss YYYY',
            '%x': 'MM/DD/YYYY',
            '%X': 'HH:mm:ss',
            '%%': '%'
        }

        for p_format, m_format in mapping.items():
            format = format.replace(p_format, m_format)

        return format

    def convert_python_to_django_template(self, format):
        mapping = {
            '%d': 'd',  # Day of the month, 2 digits with leading zeros.
            '%m': 'm',  # Month, 2 digits with leading zeros.
            '%y': 'y',  # Year, 2 digits.
            '%Y': 'Y',  # Year, 4 digits.
            '%H': 'H',  # Hour, 24-hour format.
            '%M': 'i',  # Minutes
            '%S': 's',  # Seconds, 2 digits with leading zeros.
            '%p': 'A',  # 'AM' or 'PM'
        }

        for p_format, m_format in mapping.items():
            format = format.replace(p_format, m_format)

        return format


class TimePicker(DateTimePicker):
    format = 'H:m'
    show_today_button = False
    glyphicon = 'glyphicon-time'
