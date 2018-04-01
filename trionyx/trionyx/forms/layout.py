"""
trionyx.trionyx.forms.layout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from crispy_forms.layout import Field


class TimePicker(Field):
    """
    Render field with timepicker: https://jdewit.github.io/bootstrap-timepicker/

    Example:

    .. code:: python

        TimePicker('time_field', minute_step=10, show_inputs=False)
    """

    template = 'trionyx/forms/timepicker.html'

    max_hours = 24
    """Specify a maximum number of hours the TimePicker can handle. showMeridian must be set to false"""

    snap_to_step = False
    """
    If true, setting the time will snap it to the closest "step",
    either minute or second, depending on which unit is currently highlighted.
    If the number would otherwise snap to 60 higher, the unit "overflows" to 0
    """

    minute_step = 15
    """Specify a step for the minute field"""

    show_seconds = False
    """Show the seconds field"""

    default_time = 'current'
    """
    Set default time options are:

    - `'current'`: Set to the current time
    - `'11:45'`: Set to a specific time
    - `False`: Do not set a default time
    """

    show_meridian = False
    """When True show 12h mode on False show 24h mode"""

    show_inputs = True
    """When True Shows the text inputs in the widget."""

    disable_focus = False
    """Disables the input from focusing. This is useful for touch screen devices that display a keyboard on input focus"""

    valid_options = [
        'max_hours',
        'snap_to_step',
        'minute_step',
        'show_seconds',
        'default_time',
        'show_meridian',
        'show_inputs',
        'disable_focus',
    ]

    def __init__(self, field, **kwargs):
        """Transform options to data options and add css class"""
        for key in self.valid_options:
            kwargs['data-{}'.format(key)] = str(kwargs.pop(key, getattr(self, key))).lower()

        kwargs['css_class'] = '{} timepicker'.format(kwargs.get('css_class', '')).strip()
        super().__init__(field, **kwargs)
