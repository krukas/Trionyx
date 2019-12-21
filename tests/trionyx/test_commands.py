import os
import shutil
import tempfile
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase


class CommandsTest(TestCase):
    temp_dir = os.path.join(tempfile.gettempdir(), 'trionyx_temp')

    def setUp(self):
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
        os.mkdir(self.temp_dir)

    def test_generate_theme_css(self):
        out = StringIO()
        call_command('generate_theme_css', stdout=out)

        self.assertIn('.bg-theme', out.getvalue())

    def test_create_app(self):
        with self.settings(BASE_DIR=self.temp_dir):
            out = StringIO()
            call_command('create_app', 'new_app', stdout=out)

        self.assertTrue(os.path.isfile(os.path.join(self.temp_dir, 'apps', 'new_app', 'migrations', '__init__.py')))

    def test_create_app_already_exists(self):
        with self.settings(BASE_DIR=self.temp_dir):
            out = StringIO()
            call_command('create_app', 'new_app', stdout=out)
            self.assertRaises(CommandError, call_command, 'create_app', 'new_app', stdout=out)
