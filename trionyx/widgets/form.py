"""
trionyx.widgets.form
~~~~~~~~~~~~~~~~~~~~

Package containing all the from node widgets

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
from . import Node


class Fieldset(Node):
    """
    Form fieldset widget

    Config options:
        -title
    """

    config = {
        'title': {'blank': False}
    }


class Input(Node):
    """Input form widget"""

    pass


class Textearea(Input):
    """Textearea form widget"""

    pass


class Wysiwyg(Input):
    """Wysiwyg form widget"""

    pass


class Date(Input):
    """Date form widget"""

    pass


class Form(Node):
    """Form widget"""

    valid_child_nodes = [Fieldset, Input]

    config = {
        'fields': {},
    }
