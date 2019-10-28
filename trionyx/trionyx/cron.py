"""
trionyx.trionyx.cron
~~~~~~~~~~~~~~~~~~~~

:copyright: 2019 by Maikel Martens
:license: GPLv3
"""
from datetime import timedelta


schedule = {
    'cleanup_unexpectedly_stopped_tasks': {
        'task': 'trionyx.trionyx.tasks.cleanup_unexpectedly_stopped_tasks',
        'schedule': timedelta(minutes=15)
    }
}
