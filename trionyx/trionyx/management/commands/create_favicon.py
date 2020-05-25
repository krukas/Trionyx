"""
trionyx.trionyx.management.commands.create_favicon
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Command for creating favicon"""

    help = 'Create favicon'

    def handle(self, *args, **options):
        """Create new favicon"""
        print('Deprecated, favicon is generated inline as base64')
