"""
trionyx.widgets.widgets
~~~~~~~~~~~~~~~~~~~~~~~

Package containing all the widgets

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
from . import Node


class Panel(Node):
    """Panel widget"""

    config = {
        'title': {'blank': False}
    }


class ListTable(Node):
    """
    List table widget

    Config options:
        - fields
        - editable
        - pagination
        - sortable
        - enumeration
    """

    config = {
        'fields': {'blank': False},
        'editable': {'default': True},
        'pagination': {'default': True},
        'sortable': {'default': True},
        'enumeration': {'default': True},
    }


class DataTable(Node):
    """Data table widget"""

    config = {
        'fields': {},
    }
