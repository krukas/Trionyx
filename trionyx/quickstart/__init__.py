"""
trionyx.quickstart
~~~~~~~~~~~~~~~~~~

Quickstart Trionyx project and apps

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import os
import shutil

import trionyx
from trionyx import utils


class Quickstart:
    """Class for creating Trionyx project and apps"""

    def __init__(self):
        """Set project template paths"""
        quickstart_path = os.path.realpath(__file__)

        self.project_path = os.path.join(os.path.dirname(quickstart_path), 'project')
        """Path to project template files"""

    def create_project(self, project_path):
        """
        Create Trionyx project in given path

        :param str path: path to create project in.
        :raises FileExistsError:
        """
        shutil.copytree(self.project_path, project_path)

        self.update_file(project_path, 'requirements.txt', {
            'trionyx_version': trionyx.__version__
        })

        self.update_file(project_path, 'config/local_settings.py', {
            'secret_key': utils.random_string(32)
        })

    def update_file(self, project_path, file_path, variables):
        """
        Update given file with given variables, variables in file must be inclosed with [[]].

        For example you want to replace a variable secret_key, in the file its [[secret_key]].

        :param str project_path:
        :param str file_path:
        :param dict variables:
        """
        update_file = os.path.join(project_path, file_path)
        with open(update_file, 'rb') as _file:
            file_content = _file.read().decode('utf-8')

        for key, value in variables.items():
            file_content = file_content.replace('[[{}]]'.format(key), value)

        with open(update_file, 'w+', encoding='utf-8') as _file:
            _file.writelines(file_content)
