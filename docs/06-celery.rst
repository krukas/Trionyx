Celery background tasks
=======================

Trionyx uses Celery for background tasks,
for full documentation go to `Celery 4.1 documentation <http://docs.celeryproject.org/en/latest/index.html>`_.


Configuration
-------------

Default there is no configuration required if standard RabbitMQ server is installed on same server.
Default broker url is: `amqp://guest:guest@localhost:5672//`

.. note::
    if you want to use other broker or multiple queue's look at the Celery documentation.


Creating background task
------------------------

Tasks mused by defined in the file `tasks.py` in your Django app. Tasks in the tasks.py will by auto detected by Celery.

Example of a task with arguments:

.. code-block:: python

    from celery import shared_task

    @shared_task
    def send_email(email):
        # Send email

    # You can call this task normally by:
    send_email('test@example.com')

    # Or you can run this task in the background by:
    send_email.delay('test@example.com')


Running task periodically (cron)
--------------------------------

You can run a task periodically by defining a schedule in the `cron.py` in you Django app.

.. code-block:: python

    from celery.schedules import crontab

    schedule = {
        'spammer': {
            'task': 'app.test.tasks.send_email',
            'schedule': crontab(minute='*'),
        }
    }


Running celery (development)
----------------------------

If you have a working broker installed and configured you can run celery with:

.. code-block:: bash

    celery worker -A celery_app -B -l info


Live setup (systemd)
--------------------

For live deployment you want to run celery as a daemon,
`more info in the Celery documentation <http://docs.celeryproject.org/en/latest/userguide/daemonizing.html#daemonizing>`_


celery.service
~~~~~~~~~~~~~~

/etc/systemd/system/celery.service

.. code-block:: ini

    [Unit]
    Description=Celery Service
    After=network.target

    [Service]
    Type=forking
    # Change this to Username and group that Trionyx project is running on.
    User=celery
    Group=celery

    EnvironmentFile=-/etc/conf.d/celery

    # Change this to root of your Trionyx project
    WorkingDirectory=/root/of/trionyx/projext

    ExecStart=/bin/sh -c '${CELERY_BIN} multi start ${CELERYD_NODES} \
      -A ${CELERY_APP} --pidfile=${CELERYD_PID_FILE} \
      --logfile=${CELERYD_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} ${CELERYD_OPTS}'
    ExecStop=/bin/sh -c '${CELERY_BIN} multi stopwait ${CELERYD_NODES} \
      --pidfile=${CELERYD_PID_FILE}'
    ExecReload=/bin/sh -c '${CELERY_BIN} multi restart ${CELERYD_NODES} \
      -A ${CELERY_APP} --pidfile=${CELERYD_PID_FILE} \
      --logfile=${CELERYD_LOG_FILE} --loglevel=${CELERYD_LOG_LEVEL} ${CELERYD_OPTS}'

    [Install]
    WantedBy=multi-user.target



Configuration file
~~~~~~~~~~~~~~~~~~

/etc/conf.d/celery

.. code-block:: ini

    CELERYD_NODES="worker1"

    # Absolute or relative path to the 'celery' command:
    CELERY_BIN="/usr/local/bin/celery"

    CELERY_APP="celery_app"

    # Extra command-line arguments to the worker
    CELERYD_OPTS="--concurrency=8"

    # - %n will be replaced with the first part of the nodename.
    # - %I will be replaced with the current child process index
    #   and is important when using the prefork pool to avoid race conditions.
    CELERYD_PID_FILE="/var/run/celery/%n.pid"
    CELERYD_LOG_FILE="/var/log/celery/%n%I.log"
    CELERYD_LOG_LEVEL="INFO"


.. note::

    Make sure that the PID and LOG file directory is writable for the user that is running Celery.