from django.test import TestCase
from django.utils import timezone
from django.conf import settings

from trionyx.trionyx.models import Task, User
from trionyx.trionyx.tasks import cleanup_unexpectedly_stopped_tasks, MassUpdateTask


class TasksTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            email='info@trionyx.com'
        )
        self.user2 = User.objects.create(
            email='test@test.com'
        )

    def test_mass_update(self):
        Task.objects.create(
            celery_task_id='running-in-time',
            status=Task.RUNNING,
            started_at=timezone.now()
        )
        failed_task = Task.objects.create(
            celery_task_id='running-not-in-time',
            status=Task.RUNNING,
            started_at=timezone.now() - timezone.timedelta(seconds=settings.CELERY_TASK_TIME_LIMIT * 2)
        )

        cleanup_unexpectedly_stopped_tasks()

        failed_task.refresh_from_db()
        self.assertEqual(failed_task.status, Task.FAILED)

    def test_mass_update_selected(self):
        MassUpdateTask().delay(
            all='0',
            ids=str(self.user1.id),
            filters='[]',
            data={
                'first_name': 'new name'
            },

            task_model=User,
        )

        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.assertEqual(self.user1.first_name, 'new name')
        self.assertEqual(self.user2.first_name, '')

    def test_mass_update_filter_all(self):
        MassUpdateTask().delay(
            all='1',
            ids='',
            filters='[{"field": "email", "operator": "==", "value": "test@test.com"}]',
            data={
                'first_name': 'new name'
            },

            task_model=User,
        )

        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.assertEqual(self.user1.first_name, '')
        self.assertEqual(self.user2.first_name, 'new name')

    def test_mass_update_all(self):
        MassUpdateTask().delay(
            all='1',
            ids='',
            filters='[]',
            data={
                'first_name': 'new name'
            },

            task_model=User,
        )

        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.assertEqual(self.user1.first_name, 'new name')
        self.assertEqual(self.user2.first_name, 'new name')
