"""
trionyx.widgets.layout
~~~~~~~~~~~~~~~~~~~~~~

Package containing all the layout node widgets

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
from . import Node


class Tab(Node):
    """Tab widget"""

    pass


class EmptyLayout(Node):
    """Empty layout widget"""

    pass


class TabLayout(EmptyLayout):
    """Tab layout widget"""

    valid_child_nodes = [Tab]
