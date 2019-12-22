How to write reusable apps
==========================

Trionyx support auto registering off reusable apps with the setup entry_points.
This means you only have to `pip install <reusable app>` in your Trionyx project
and it will be auto loaded into project, no further configuration needed.

Create reusable app
-------------------

To create a complete working base structure for your reusable app run:

.. code-block:: bash

    trionyx create_reusable_app <name>

You now can create your Trionyx app how you do normally.
And when you are ready with your first version you can upload it to PyPi.