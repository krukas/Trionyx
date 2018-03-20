"""
trionyx.navigation
~~~~~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""


class Menu:
    """Meu class that hold the root tree item"""

    _root_item = None

    @classmethod
    def add_item(cls, path, name, icon=None, url=None, order=None, permission=None):
        """
        Add new menu item to menu

        :param path: Path of menu
        :param name: Display name
        :param icon: CSS icon
        :param url: link to page
        :param order: Sort order
        :param permission:
        :return:
        """
        if cls._root_item is None:
            cls._root_item = MenuItem('ROOT', 'ROOT')

        root_item = cls._root_item
        current_path = ''
        for node in path.split('/')[:-1]:
            if not node:
                continue

            current_path = '/' + '{}/{}'.format(current_path, node).strip('/')
            new_root = root_item.child_by_code(node)
            if not new_root:  # Create menu item if not exists
                new_root = MenuItem(current_path, name=str(node).capitalize())
                root_item.add_child(new_root)
            root_item = new_root

        new_item = MenuItem(path, name, icon, url, order, permission)

        current_item = root_item.child_by_code(path.split('/')[-1])
        if current_item:
            current_item.merge(new_item)
        else:
            root_item.add_child(new_item)

    @classmethod
    def get_menu_items(cls):
        """Get menu items"""
        if not cls._root_item:
            return[]
        return cls._root_item.childs


class MenuItem:
    """Menu item that holds all menu item data"""

    def __init__(self, path, name, icon=None, url=None, order=None, permission=None):
        """
        Init menu item

        :param path: Path of menu
        :param name: Display name
        :param icon: CSS icon
        :param url: link to page
        :param order: Sort order
        :param permission:
        """
        self.path = path
        self.name = name
        self.icon = icon
        self.url = url
        self.order = order
        self.permission = permission

        self.depth = 1
        self.childs = []

    def merge(self, item):
        """Merge Menu item data"""
        self.name = item.name

        if item.icon:
            self.icon = item.icon

        if item.url:
            self.url = item.url

        if item.order:
            self.order = item.order

        if item.permission:
            self.permission = item.permission

    def add_child(self, item):
        """Add child to menu item"""
        index = 0
        if item.order is not None:
            for child in self.childs:
                if child.order is None or item.order < child.order:
                    break
                index += 1
        else:
            index = len(self.childs)

        item.depth = self.depth + 1
        self.childs = self.childs[:index] + [item] + self.childs[index:]

    def child_by_code(self, code):
        """
        Get child MenuItem by its last path code

        :param code:
        :return: MenuItem or None
        """
        for child in self.childs:
            if child.path.split('/')[-1] == code:
                return child
        return None
