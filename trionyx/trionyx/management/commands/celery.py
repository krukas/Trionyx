"""
trionyx.trionyx.management.commands.celery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2020 by Maikel Martens
:license: GPLv3
"""
import shlex
import subprocess

from django.core.management.base import BaseCommand
from django.utils import autoreload


class Command(BaseCommand):
    """Command to start Celery with autoreload function"""

    def add_arguments(self, parser):
        """Add name argument"""
        parser.add_argument('celery_app', type=str, default='celery_app', nargs='?')

    def handle(self, *args, **options):
        """Start Celery"""

        def restart_celery():
            """Restart celery worker"""
            print('Starting celery worker with autoreload...')
            cmd = 'pkill -9 celery'
            subprocess.call(shlex.split(cmd))
            cmd = 'celery worker -A {} -l info'.format(options.get('celery_app'))
            subprocess.call(shlex.split(cmd))

        autoreload.run_with_reloader(restart_celery)
