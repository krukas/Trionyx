"""
trionyx.navigation
~~~~~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import re
import copy

from django.apps import apps
from django.urls import reverse

from trionyx.config import models_config


class Menu:
    """Meu class that hold the root tree item"""

    def __init__(self, root_item=None):
        """Init Menu"""
        self.root_item = root_item

    def auto_load_model_menu(self):
        """
        Auto load model menu entries, can be configured in `trionyx.config.ModelConfig`:

        - menu_name
        - menu_icon
        - menu_order
        """
        from trionyx.trionyx.apps import BaseConfig

        order = 0
        for app in apps.get_app_configs():
            if not isinstance(app, BaseConfig) or getattr(app, 'no_menu', False):
                continue

            app_path = app.name.split('.')[-1]
            model_order = 0
            for model in app.get_models():
                config = models_config.get_config(model)

                if config.menu_exclude:
                    continue

                menu_icon = None
                menu_path = '{}/{}'.format(app_path, config.model_name)
                if config.menu_root:
                    order += 10
                    menu_order = order
                    menu_icon = config.menu_icon
                    menu_path = config.model_name
                else:
                    model_order += 10
                    menu_order = model_order

                self.add_item(
                    path=menu_path,
                    name=config.menu_name if config.menu_name else model._meta.verbose_name_plural.capitalize(),
                    order=config.menu_order if config.menu_order else menu_order,
                    icon=menu_icon,
                    url=reverse(
                        "trionyx:model-list",
                        kwargs={
                            'app': model._meta.app_label,
                            'model': model._meta.model_name,
                        }
                    ),
                    permission='{app_label}.view_{model_name}'.format(
                        app_label=config.app_label,
                        model_name=config.model_name,
                    ).lower()
                )

            if model_order > 0:
                order += 10
                self.add_item(
                    path=app_path,
                    name=getattr(app, 'menu_name', app.verbose_name),
                    icon=getattr(app, 'menu_icon', None),
                    order=getattr(app, 'menu_order', order),
                )

    def add_item(self, path, name, icon=None, url=None, order=None, permission=None, active_regex=None):
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
        if self.root_item is None:
            self.root_item = MenuItem('ROOT', 'ROOT')

        root_item = self.root_item
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

        new_item = MenuItem(path, name, icon, url, order, permission, active_regex)

        current_item = root_item.child_by_code(path.split('/')[-1])
        if current_item:
            current_item.merge(new_item)
        else:
            root_item.add_child(new_item)

    def get_menu_items(self, user=None):
        """Get menu items"""
        if not self.root_item:
            return []

        def filter_childs(childs):
            menu = []
            for item in childs:
                if not item.permission or (item.permission and user.has_perm(item.permission)):
                    item = copy.copy(item)
                    if item.childs:
                        item.childs = filter_childs(item.childs)
                        if item.childs:
                            menu.append(item)
                    else:
                        menu.append(item)

            return menu

        return filter_childs(self.root_item.childs)


class MenuItem:
    """Menu item that holds all menu item data"""

    def __init__(self, path, name, icon=None, url=None, order=None, permission=None, active_regex=None):
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
        self.active_regex = active_regex

        self.depth = 0
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
        item.depth = self.depth + 1
        self.childs.append(item)
        self.childs = sorted(self.childs, key=lambda item: item.order if item.order else 999)

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

    def is_active(self, path):
        """Check if given path is active for current item"""
        if self.url == '/' and self.url == path:
            return True
        elif self.url == '/':
            return False

        if self.url and path.startswith(self.url):
            return True

        if self.active_regex and re.compile(self.active_regex).match(path):
            return True

        for child in self.childs:
            if child.is_active(path):
                return True
        return False


app_menu = Menu()
add_menu_item = app_menu.add_item
