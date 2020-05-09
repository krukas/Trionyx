"""
trionyx.tasks
~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import logging
from datetime import datetime

import celery
from celery import shared_task, current_app  # noqa F401
from celery.utils import uuid
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from trionyx.models import get_class
from trionyx.utils import CacheLock, get_current_request

Task = get_class('trionyx.Task')

logger = logging.getLogger(__name__)


class TaskMetaClass(type):
    """MetaClass for task"""

    def __new__(cls, clsname, bases, attrs):
        """Auto register celery task"""
        TaskClass = super().__new__(cls, clsname, bases, attrs)

        if clsname != 'BaseTask':
            current_app.tasks.register(TaskClass())

        return TaskClass


class BaseTask(celery.Task, metaclass=TaskMetaClass):
    """Trionyx BaseTask"""

    name = ''
    task_queue = None
    task_description = _('Base Task')
    task_lock = True
    task_model = None

    default_countdown = 2
    """Prevent task run to soon and transaction is not committed, this will happen if you use post_save signal"""

    def __call__(self, *args, **kwargs):
        """Run task"""
        self.__task, _ = Task.objects.get_or_create(celery_task_id=self.request.id)

        if self.__task.object_id and self.task_lock:
            with CacheLock('TASK_LOCK', self.__task.object_type_id, self.__task.object_id, timeout=settings.CELERY_TASK_TIME_LIMIT + 60):
                return self._run(*args, **kwargs)
        else:
            return self._run(*args, **kwargs)

    def _run(self, *args, **kwargs):
        """Run task and save result"""
        self.__task.status = Task.RUNNING
        self.__task.started_at = timezone.now()
        self.__task.save()

        try:
            if self.__task.user:
                with self.__task.user.locale_override():
                    result = super().__call__(*args, **kwargs)
                    if not result:
                        result = str(_('Task completed'))
            else:
                result = super().__call__(*args, **kwargs)
                if not result:
                    result = _('Task completed')

            duration = timezone.now() - self.__task.started_at
            self.__task.execution_time = int(duration.total_seconds())
            self.__task.result = str(result)
            self.__task.progress = 100
            self.__task.status = Task.COMPLETED
            self.__task.save()
        except Exception as e:
            logger.exception(e)
            result = str(e)

            self.__task.result = result
            self.__task.status = Task.FAILED
            self.__task.progress = 100
            self.__task.save()

        return result

    def delay(self, *args, **kwargs):
        """Start task"""
        task_id = uuid()
        user = kwargs.pop('task_user', None)
        description = kwargs.pop('task_description', self.task_description)
        object = kwargs.pop('task_object', None)
        model = kwargs.pop('task_model', self.task_model)
        eta = kwargs.pop('task_eta', None)
        queue = kwargs.pop('task_queue', self.task_queue)

        eta = eta if isinstance(eta, datetime) else None
        countdown = self.default_countdown if eta is None else None
        model = object if object else model

        if not user and get_current_request() and get_current_request().user.is_authenticated:
            user = get_current_request().user

        Task.objects.create(
            celery_task_id=task_id,
            description=description,
            identifier=self.name,
            object_id=object.id if object else None,
            object_type=ContentType.objects.get_for_model(model) if model else None,
            object_verbose_name=str(object) if object else '',
            user=user,
            status=Task.SCHEDULED if eta else Task.QUEUE,
            scheduled_at=eta,
        )

        return self.apply_async(args=args, kwargs=kwargs, task_id=task_id, eta=eta, queue=queue, countdown=countdown)

    def set_progress(self, progress):
        """Set progress"""
        progress = progress if progress > 0 else 0
        progress = progress if progress <= 100 else 100

        self.__task.progress = progress
        self.__task.save()

    def add_output(self, output):
        """Add task process output"""
        logger.info('TASK OUTPUT: {output}'.format(output=output))
        self.__task.progress_output.append(output)
        self.__task.save()

    def get_user(self):
        """Return task user"""
        return self.__task.user

    def get_object(self):
        """Return task object"""
        return self.__task.object

    def get_model(self):
        """Return task model"""
        if self.__task.object_type:
            return self.__task.object_type.model_class()
        return None
