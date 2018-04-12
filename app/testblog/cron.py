from datetime import timedelta

schedule = {
    'every-minute': {
        'task': 'app.testblog.tasks.cron_task',
        'schedule': timedelta(minutes=1)
    }
}