Getting started
===============

Django already gives a solid foundation for building apps.
Trionyx add some improvements like auto loading signals/forms/cron's.
It also add new things as default views/api/background tasks (celery).

In this *getting started* guide we will create a new app,
to show you a little of the basics on how Trionyx work and what it can do.

**This guide assumes you have followed the** :doc:`installation instructions </trionyx/installation>`,
**and you are now in the root of your new project with the virtual environment active**

*This guide requires no previous knowledge of Django,
but it wont go in depth on how Django works*

Your first app
~~~~~~~~~~~~~~

First we need to create a new app.
Default Trionyx structure all apps go in the **apps** folder.
To create a base app use the following manage command:

.. code-block:: bash

    ./manage.py create_app knowledgebase

In your apps folder should be your new app knowledgebase

    -
    -

Explain file structure + possible new files cron/signals/tasks/layouts


File structure
~~~~~~~~~~~~~~

  :doc:`cron </trionyx/celery>`



Create model
~~~~~~~~~~~~



Model configuration
~~~~~~~~~~~~~~~~~~~

Custom Form
~~~~~~~~~~~

Custom Layout
~~~~~~~~~~~~~

Explain add tab to user model

Signals
~~~~~~~
Send new email on comment

Background Task
~~~~~~~~~~~~~~~
Create cron task to say hello ever day to all users

Dashboard Widget
~~~~~~~~~~~~~~~~
Explain default widget, create widget with latest articles

API
~~~
Custom serializer


I hope you have a better understanding on how Trionyx works.
And that it can help you build you business application with the focus on your data and processes.
