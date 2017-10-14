"""
trionyx.widgets
~~~~~~~~~~~~~~~

Package containing all the node widgets

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""


class NodeError(Exception):
    """Node error Exception"""

    pass


class Node:
    """Node widget for rendering views"""

    valid_child_nodes = None
    code = None
    config = {
        'title': {},
        'grid_column': {'default': 'L12'},
    }

    def __init__(self, **kwargs):
        """Init node and get config values from kwargs"""
        self.children = kwargs.pop('children', [])
        """Children of node"""

        self.data = {}
        """Date for node, date is set with kwargs"""

        self.set_data(kwargs)

        if type(self.children) is not list:
            self.children = [self.children]

        if self.valid_child_nodes:
            valid_nodes = [n.get_code() for n in self.valid_child_nodes]
            for child in self.children:
                if child.get_code() not in valid_nodes:
                    raise Exception('({}) is not a valid child for ({})'.format(child.get_code(), self.get_code()))

    @classmethod
    def get_all_configs(cls):
        """
        Get all configs from node, combines all __base__ class config till Node class.

        :return: complete config of Node
        :rtype: dict
        """
        config = cls.config
        current_class = cls.__base__

        while hasattr(current_class, 'config'):
            for key, value in current_class.config.items():
                if key not in config:
                    config[key] = value
            current_class = current_class.__base__

        return config

    @classmethod
    def get_code(cls):
        """
        Give the Node code, if no code is set it will returns lowercase of class name.

        :return: Node code
        :rtype: str
        """
        if cls.code:
            return cls.code
        return cls.__name__.lower()

    @classmethod
    def get_inheritance_tree(cls):
        """
        Give a list Node inheritance codes.

        :return: List of inheritance nodes
        :rtype: list
        """
        # TODO cls support for mixins __bases__
        inheritance_tree = [cls.get_code()]

        current_class = cls.__base__
        while issubclass(current_class, Node):
            inheritance_tree.append(current_class.get_code())
            current_class = current_class.__base__

        return inheritance_tree

    def set_data(self, kwargs):
        """
        Set data based on kwargs and valid configs for Node.

        :param kwargs:
        """
        config = self.get_all_configs()

        # Set default values
        for key, value in config.items():
            if value.get('default'):
                self.data[key] = value.get('default')

        for key, value in kwargs.items():
            if key in config:
                if not config[key].get('blank', True) and not value:
                    raise NodeError('Value is not set or is empty for {}'.format(key))
                self.data[key] = value
            else:
                raise NodeError('Option ({}) is not a valid option for ({})'.format(key, self.get_code()))

    def to_config(self):
        """
        Convert Node tree to dict config tree

        :return: Node config tree
        :rtype: dict
        """
        children = []

        for child in self.children:
            children.append(child.to_config())

        return {
            'node_code': self.get_code(),
            'inheritance_tree': self.get_inheritance_tree(),
            **self.data,
            'children': children,
        }
