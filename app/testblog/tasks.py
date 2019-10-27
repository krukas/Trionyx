import time
from celery import shared_task
from django.utils import timezone
from trionyx.tasks import BaseTask

@shared_task
def manual_task(some_input):
    print(some_input)

@shared_task
def cron_task():
    print('run cron task')

class PostTask(BaseTask):
    name = 'post_publish'
    task_description = 'Post publish'

    def run(self):
        if not self.get_object():
            raise Exception('No object')

        for x in range(100):
            time.sleep(0.25)

            self.set_progress(x)

            if x % 10 == 0:
                self.add_output('Process at {}%'.format(x))

        object = self.get_object()
        object.publish_date = timezone.now()
        object.save()

        return object.publish_date