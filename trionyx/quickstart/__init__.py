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

import yaml
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

        self.reusable_app_path = os.path.join(os.path.dirname(quickstart_path), 'reusable_app')
        """Path to reusable app template files"""

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

        app_name = os.path.basename(project_path).capitalize()

        self.update_file(project_path, 'README.rst', {
            'title': "{name}\n{heading}".format(
                name=app_name,
                heading='=' * len(app_name),
            )
        })

        self.update_file(project_path, 'config/settings/base.py', {
            'app_name': app_name,
            'logo_name_start': app_name[0],
            'logo_name_end': app_name[1:],
            'logo_name_small_start': app_name[0].upper(),
            'logo_name_small_end': app_name[1].upper(),
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

    def create_reusable_app(self, path, name):
        """
        Create Trionyx reusable app

        :param path:
        :param name:
        :return:
        """
        shutil.copytree(self.reusable_app_path, path)

        variables = {
            'name': name.lower(),
            'verbose_name': name.capitalize(),
        }

        self.update_file(path, '[app_name]/apps.py', variables)
        self.update_file(path, '[app_name]/__init__.py', variables)
        self.update_file(path, 'app/settings.py', variables)
        self.update_file(path, 'MANIFEST.in', variables)
        self.update_file(path, 'README.rst', variables)
        self.update_file(path, 'setup.py', variables)

        # Rename package
        shutil.move(os.path.join(path, '[app_name]'), os.path.join(path, name.lower()))

    def create_ansible(self, project_path, domain, repo):
        """Create Ansible live deploy script"""
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
            'ansible_ssh_user': 'ansible',
            'ansible_ssh_port': 6969,
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
