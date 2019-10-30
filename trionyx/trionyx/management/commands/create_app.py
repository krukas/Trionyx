"""
trionyx.trionyx.management.commands.create_app
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from trionyx.quickstart import Quickstart


class Command(BaseCommand):
    """Command for creating base Trionyx app"""

    help = 'Create base app'

    def add_arguments(self, parser):
        """Add name argument"""
        parser.add_argument('name', type=str)

    def handle(self, *args, **options):
        """Create new app"""
        quickstart = Quickstart()

        try:
            quickstart.create_app(os.path.join(settings.BASE_DIR, 'apps'), options.get('name'))
            self.stdout.write(
                self.style.SUCCESS("Successfully created app ({name}), don't forget to add 'apps.{name}' to INSTALLED_APPS".format(
                    name=options.get('name')
                ))
            )
        except FileExistsError:
            raise CommandError("App with same name already exists")
