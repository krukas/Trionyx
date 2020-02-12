"""
trionyx.utils
~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import time
import logging
import random
import string
import importlib
import hashlib
from functools import reduce
from typing import List, Any, Optional

from django.conf import settings
from django.utils import translation
from django.utils import formats
from django.core.cache import cache

logger = logging.getLogger(__name__)


class CacheLock:
    """CacheLock uses the django cache to give a lock for given keys"""

    def __init__(self, *keys: Any, timeout: Optional[int] = None):
        """Init CacheLock"""
        self.keys = keys
        self.timeout = timeout

    @property
    def cache_key(self) -> str:
        """Cache key"""
        return 'trionyx-cache-lock-{key}'.format(
            key=hashlib.md5(''.join([str(k) for k in self.keys]).encode()).hexdigest()
        )

    def __enter__(self):
        """Acquire lock"""
        run_time = 0
        wait_time = 0.1
        while not cache.add(self.cache_key, 'true', 999999):
            if self.timeout and run_time > self.timeout:
                raise TimeoutError()
            time.sleep(wait_time)
            run_time += wait_time

    def __exit__(self, *args, **kwargs):
        """Clear cache lock"""
        cache.delete(self.cache_key)


def random_string(size: int) -> str:
    """Create random string containing ascii leters and digits, with the length of given size"""
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))


def import_object_by_string(namespace: str) -> Any:
    """Import object by complete namespace"""
    segments = namespace.split('.')
    module = importlib.import_module('.'.join(segments[:-1]))
    return getattr(module, segments[-1])


def create_celerybeat_schedule(apps: List[str]) -> dict:
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

        module_schedule = getattr(module, 'schedule', None)
        if not isinstance(module_schedule, dict):
            logger.warning('{} has no schedule or schedule is not a dict'.format(module.__name__))
            continue

        # Add cron queue option
        for name, schedule in module_schedule.items():
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


def get_current_request():
    """Get current request object"""
    from trionyx.trionyx import LOCAL_DATA
    return getattr(LOCAL_DATA, 'request', None)


def get_app_version():
    """Get app version"""
    try:
        from config import __version__  # type: ignore
        return __version__
    except ImportError:
        return None
