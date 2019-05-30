"""
trionyx.utils
~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import logging
import random
import string
import importlib
from functools import reduce

from django.conf import settings
from django.utils import translation
from django.utils import formats

logger = logging.getLogger(__name__)


def random_string(size):
    """Create random string containing ascii leters and digits, with the length of given size"""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))


def import_object_by_string(namespace):
    """Import object by complete namespace"""
    segments = namespace.split('.')
    module = importlib.import_module('.'.join(segments[:-1]))
    return getattr(module, segments[-1])


def create_celerybeat_schedule(apps):
    """Create Celery beat schedule by get schedule from every installed app"""
    beat_schedule = {}
    for app in apps:
        try:
            config = import_object_by_string(app)
            module = importlib.import_module('{}.cron'.format(config.name))
        except Exception:
            try:
                module = importlib.import_module('{}.cron'.format(app))
            except Exception:
                continue

        if not (hasattr(module, 'schedule') and isinstance(module.schedule, dict)):
            logger.warning('{} has no schedule or schedule is not a dict'.format(module.__name__))
            continue

        # Add cron queue option
        for name, schedule in module.schedule.items():
            options = schedule.get('options', {})
            if 'queue' not in options:
                options['queue'] = 'cron'
                schedule['options'] = options

                beat_schedule[name] = schedule

    return beat_schedule


def get_current_language():
    """Get active language by django.utils.translation or return settings LANGUAGE_CODE"""
    if translation.get_language():
        return translation.get_language()
    return settings.LANGUAGE_CODE


def get_current_locale():
    """Get active locale based on get_current_language function"""
    return translation.to_locale(get_current_language())


def get_datetime_input_format(date_only=False):
    """
    Get current locale date input format.

    :param date_only:
    :return:
    """
    return formats.get_format_lazy('DATE_INPUT_FORMATS' if date_only else 'DATETIME_INPUT_FORMATS')[0]


def datetime_format_to_momentjs(format):
    """
    Convert python datetime string format to momentjs string format.

    :param format: python datetime string format
    :return:
    """
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
    return reduce(lambda value, key: value.replace(key, mapping[key]), mapping.keys(), format)


def datetime_format_to_django_template(format):
    """
    Convert python datetime string format to django template string format.

    :param format: python datetime string format
    :return:
    """
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
    return reduce(lambda value, key: value.replace(key, mapping[key]), mapping.keys(), format)
