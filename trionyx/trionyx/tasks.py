"""
trionyx.trionyx.tasks
~~~~~~~~~~~~~~~~~~~~~

:copyright: 2019 by Maikel Martens
:license: GPLv3
"""
import json
import math

from django.conf import settings
from django.utils import timezone
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

from trionyx.trionyx.models import Task
from trionyx.tasks import shared_task, BaseTask
from trionyx.models import filter_queryset_with_user_filters


@shared_task
def cleanup_unexpectedly_stopped_tasks():
    """Set tasks that are unexpectedly stopped to failed"""
    Task.objects.filter(
        started_at__lt=timezone.now() - timezone.timedelta(seconds=settings.CELERY_TASK_TIME_LIMIT + 60),
        status__in=[Task.RUNNING, Task.LOCKED]
    ).update(
        status=Task.FAILED,
        result=_("Task unexpectedly stopped")
    )


class MassUpdateTask(BaseTask):
    """Mass update task"""

    name = 'mass_update'

    def run(self, all, ids, filters, data):
        """Run mass update"""
        query = self.get_model().objects.get_queryset()

        if all == '1':
            query = filter_queryset_with_user_filters(query, json.loads(filters))
        else:
            query = query.filter(id__in=[int(id) for id in filter(None, ids.split(','))])

        count = query.count()
        errors = []
        for index, obj in enumerate(query.iterator(100)):
            for key, value in data.items():
                setattr(obj, key, value)

            try:
                obj.clean()
                obj.save()
            except ValidationError as e:
                errors.append("{}: {}".format(obj, ','.join(e.messages)))
            except Exception:
                errors.append(str(obj))
            finally:
                self.set_progress(math.ceil((index / count) * 100))

        if errors:
            raise Exception(_('Could not update the following items {}').format(', '.join(errors)))
