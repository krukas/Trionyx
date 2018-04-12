from celery import shared_task


@shared_task
def manual_task(some_input):
    print(some_input)

@shared_task
def cron_task():
    print('run cron task')