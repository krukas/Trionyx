"""
trionyx.celery
~~~~~~~~~~~~~~

:copyright: 2020 by Maikel Martens
:license: GPLv3
"""
from django.contrib.auth import get_user_model
from celery.signals import after_setup_logger, before_task_publish, task_prerun, task_postrun
from trionyx.log import enable_db_logger
from trionyx import utils


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    """Enable DB logger for celery"""
    enable_db_logger()


@before_task_publish.connect
def add_user(sender=None, headers=None, body=None, **kwargs):
    """Add user to celery"""
    user = utils.get_current_user()
    headers['__metadata__'] = {
        'trionyx_user_id': user.id if user else None
    }


@task_prerun.connect
def set_user(task_id, task, *args, **kwargs):
    """Set user to local data"""
    metadata = getattr(task.request, '__metadata__', {})
    user_id = metadata.get('trionyx_user_id')
    User = get_user_model()

    # Make sure local data is clean, before setting new data
    utils.clear_local_data()

    if user_id:
        try:
            utils.set_local_data('user', User.objects.get(id=user_id))
        except User.DoesNotExist:
            pass


@task_postrun.connect
def cleanup(*args, **kwargs):
    """Clear all local data"""
    utils.clear_local_data()
