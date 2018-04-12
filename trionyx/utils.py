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
    schedule = {}
    for app in apps:
        try:
            config = import_object_by_string(app)
            module = importlib.import_module('{}.cron'.format(config.name))
        except Exception:
            try:
                module = importlib.import_module('{}.cron'.format(app))
            except (ImportError, ModuleNotFoundError):
                continue

        if not (hasattr(module, 'schedule') and isinstance(module.schedule, dict)):
            logger.warning('{} has no schedule or schedule is not a dict'.format(module.__name__))
            continue

        schedule.update(module.schedule)

    return schedule
