import os
import shutil
import tempfile
from django.test import TestCase

from trionyx.quickstart import Quickstart
from trionyx import __version__


class QuickstartTest(TestCase):
    temp_dir = os.path.join(tempfile.gettempdir(), 'trionyx_temp')

    def setUp(self):
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass

    def assertIsFile(self, *path):
        self.assertTrue(os.path.isfile(os.path.join(self.temp_dir, *path)))

    def assertFileContains(self, path, value):
        with open(os.path.join(self.temp_dir, *(path if isinstance(path, list) else [path]))) as _file:
            self.assertIn(value, _file.read())

    def test_create_project(self):
        Quickstart().create_project(self.temp_dir)

        self.assertFileContains('requirements.txt', __version__)
        self.assertFileContains('README.rst', 'Trionyx_temp')

    def test_create_app(self):
        Quickstart().create_app(self.temp_dir, 'new_app')

        self.assertIsFile('new_app', 'migrations', '__init__.py')
        self.assertFileContains(['new_app', '__init__.py'], 'new_app')
        self.assertFileContains(['new_app', 'apps.py'], 'new_app')

    def test_create_reusable_app(self):
        Quickstart().create_reusable_app(self.temp_dir, 'new_reusable_app')

        self.assertFileContains('setup.py', 'new_reusable_app')
        self.assertIsFile('new_reusable_app', 'migrations', '__init__.py')
        self.assertFileContains(['app', 'settings.py'], 'new_reusable_app')

    def test_create_ansible(self):
        Quickstart().create_ansible(self.temp_dir, 'trionyx.org', 'git@github.com:krukas/Trionyx.git')

        self.assertIsFile('ssh_keys', 'deploy_rsa')
        self.assertIsFile('ssh_keys', 'deploy_rsa.pub')
        self.assertFileContains('production', 'trionyx.org')
        self.assertFileContains(['group_vars', 'all.yml'], 'git@github.com:krukas/Trionyx.git')
