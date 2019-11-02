from django.test import TestCase

from trionyx.tasks import BaseTask
from trionyx.trionyx.models import Task, User


class TestTask(BaseTask):
    def run(self):
        self.set_progress(50)
        self.add_output('Halfway')
        if not self.get_object():
            raise Exception('no object')

        return 'some results'


class TasksTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(email="info@trionyx.com")

    def test_task_success(self):
        TestTask().delay(
            task_object=self.user,
            task_user=self.user,
        )

        task = Task.objects.first()

        self.assertEqual(task.result, 'some results')
        self.assertEqual(task.progress_output[0], 'Halfway')

    def test_task_failed(self):
        TestTask().delay(
            task_user=self.user,
        )

        task = Task.objects.first()

        self.assertEqual(task.status, Task.FAILED)
        self.assertEqual(task.result, 'no object')
        self.assertEqual(task.progress_output[0], 'Halfway')
