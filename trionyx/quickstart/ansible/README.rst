Trionyx build/deploy playbook
=============================

This playbook will install/configure and deploy your Trionyx project to a new Ubuntu server.

Setup Ubuntu server
-------------------

First we need to do a little manual setup on the server, you can do this by running the following:

    cat >setup.sh <<EOL
    #!/usr/bin/env bash
    
    useradd -m -s /bin/bash ansible
    echo "ansible ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/99-ansible
    mkdir /home/ansible/.ssh/
    chmod 700 /home/ansible/.ssh/
    touch /home/ansible/.ssh/authorized_keys
    
    read -p 'Ansible public ssh key: ' ansible_public_key
    echo $ansible_public_key > /home/ansible/.ssh/authorized_keys
    
    chmod 600 /home/ansible/.ssh/authorized_keys
    chown ansible -Rf /home/ansible/.ssh
    
    sudo apt-get update
    sudo apt-get --assume-yes install python python-pip
    
    echo "Change SSH port to 6969 and restart ssh"
    sudo sed -i "s/#Port 22/Port 6969/" /etc/ssh/sshd_config
    sudo sed -i -r 's/#?PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
    sudo sed -i -r 's/#?PermitEmptyPasswords.*/PermitEmptyPasswords no/' /etc/ssh/sshd_config
    sudo systemctl restart sshd
    EOL
    chmod +x setup.sh
    . setup.sh

**Note: Default configurations will use the RSA keys from ssh_keys/connect_rsa, 
you can change this to use your own key**


Configuration
-------------

Add your project sensitive settings to `group_vars/all.yml` and `templates/environment.json.j2`.

There will be no email server installed on the server, 
so you also need to configure your STMP server settings.
 
**!! When you want to track/save this playbook in a repository, 
make sure you encrypt all your sensitve settings in `group_vars/all.yml` with `ansible-vault` !!**


Deploy key
----------

This playbook will use the deploy key in `ssh_keys/deploy_rsa`,
make sure you add `ssh_keys/deploy_rsa.pub` to your repository deploy keys.


Run playbook
------------

To setup and deploy your app on the server run the following command:

    ansible-playbook playbook.yml -i production


Playbook deploy only
--------------------

If you only want to deploy and not check all steps for building the server, you can do so by running:

    ansible-playbook playbook.yml -i production -t deploy
    

For more information on Ansible playbooks go to https://docs.ansible.com/