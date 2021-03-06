Deploying
=========

You can deploy your Trionyx project any way that works for your environment.
If you are just looking for a simple deployment to dedicated server (or VPS).
Trionyx provides a complete Ansible role for setting up and deploying your project to a clean Ubuntu server.

**Server setup created by Ansible**:

- Nginx (https with Letsencrypt)
- Gunicorn (gevent)
- PostgreSQL with pgbouncer
- RabbitMQ
- Firewall (ufw, fail2ban)
- Auto update with unattended-upgrades

Creating Ansible playbook
-------------------------
**Prerequisites**:

- Newly installed Ubuntu 18.04 server
- Domain name that points to that server
- Git repository of your project

Before you begin you need to install Ansible:

.. code-block:: bash

    pip install --user ansible

After you have installed Ansible you can create a Trionyx playbook by running:

.. code-block:: bash

    trionyx create_ansible <domain> <repo>

Follow the instructions and the end you will have an Ubuntu server running with your Project.


Server maintenance
~~~~~~~~~~~~~~~~~~

Security updates are automatically installed with unattended-upgrades.
For the normal system update there is an upgrade.yml playbook.

.. warning::
    The upgrade.yml playbook will restart the server if an updated package required a system reboot.

You can run the system upgrade playbook with following command:

.. code-block:: bash

    ansible-playbook upgrade.yml -i production