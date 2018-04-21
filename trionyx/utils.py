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

from django.conf import settings
from django.utils import translation

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
