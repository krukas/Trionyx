"""
trionyx.quickstart
~~~~~~~~~~~~~~~~~~

Quickstart Trionyx project and apps

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import os
import shutil
import subprocess

import trionyx
from trionyx import utils


class Quickstart:
    """Class for creating Trionyx project and apps"""

    def __init__(self):
        """Set project template paths"""
        quickstart_path = os.path.realpath(__file__)

        self.project_path = os.path.join(os.path.dirname(quickstart_path), 'project')
        """Path to project template files"""

        self.app_path = os.path.join(os.path.dirname(quickstart_path), 'app')
        """Path to app template files"""

        self.ansible_path = os.path.join(os.path.dirname(quickstart_path), 'ansible')
        """Path to Ansible template files"""

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

        self.update_file(project_path, 'environment.json', {
            'secret_key': utils.random_string(32)
        })

        self.update_file(project_path, 'README.rst', {
            'title': "{name}\n{heading}".format(
                name=os.path.basename(project_path).capitalize(),
                heading='=' * len(os.path.basename(project_path)),
            )
        })

    def create_app(self, apps_path, name):
        """
        Create Trionyx app in given path

        :param str path: path to create app in.
        :param str name: name of app
        :raises FileExistsError:
        """
        app_path = os.path.join(apps_path, name.lower())

        shutil.copytree(self.app_path, app_path)

        self.update_file(app_path, '__init__.py', {
            'name': name.lower()
        })

        self.update_file(app_path, 'apps.py', {
            'name': name.lower(),
            'verbose_name': name.capitalize()
        })

    def create_ansible(self, project_path, domain, repo):
        """Create Ansible live deploy script"""
        try:
            import yaml
        except ImportError:
            raise Exception('You need to have installed ansible')

        shutil.copytree(self.ansible_path, project_path)

        self.update_file(project_path, 'production', {
            'domain': domain,
        })

        os.mkdir(os.path.join(project_path, 'ssh_keys'))
        subprocess.check_output([
            'ssh-keygen', '-t', 'rsa', '-b', '4096', '-N', '', '-f', os.path.join(project_path, 'ssh_keys', 'deploy_rsa')
        ])
        subprocess.check_output([
            'ssh-keygen', '-t', 'rsa', '-b', '4096', '-N', '', '-f', os.path.join(project_path, 'ssh_keys', 'connect_rsa')
        ])

        with open(os.path.join(project_path, 'ssh_keys', 'deploy_rsa')) as _file:
            deploy_key = _file.read()

        config = {
            'ansible_ssh_private_key_file': 'ssh_keys/connect_rsa',
            'app_domain': domain,
            'app_repo': repo,
            'app_config_template': "{{ playbook_dir }}/templates/environment.json.j2",
            'deploy_key': deploy_key,
            'secret_key': utils.random_string(32),
            'db_password': utils.random_string(16),
            'broker_password': utils.random_string(16),
            'smtp_password': '',
        }

        self.update_file(project_path, 'group_vars/all.yml', {
            'config': yaml.dump(config, default_flow_style=False, allow_unicode=True),
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
