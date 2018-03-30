"""
trionyx.navigation
~~~~~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import re
from collections import defaultdict

from django.apps import apps
from django.urls import reverse

from trionyx.config import models_config


class Menu:
    """Meu class that hold the root tree item"""

    _root_item = None

    @classmethod
    def auto_load_model_menu(cls):
        from trionyx.core.apps import BaseConfig

        order = 0
        for app in apps.get_app_configs():
            if not isinstance(app, BaseConfig) or getattr(app, 'no_menu', False):
                continue

            order += 10
            app_path = app.name.split('.')[-1]
            cls.add_item(
                path=app_path,
                name=getattr(app, 'menu_name', app.verbose_name),
                icon=getattr(app, 'menu_icon', None),
                order=getattr(app, 'menu_order', order),
            )

            model_order = 0
            for model in app.get_models():
                config = models_config.get_config(model)
                if config.menu_exclude:
                    continue

                model_order += 10
                cls.add_item(
                    path='{}/{}'.format(app_path, model.__name__.lower()),
                    name=config.menu_name if config.menu_name else model._meta.verbose_name_plural.capitalize(),
                    order=config.menu_order if config.menu_order else model_order,
                    url=reverse(
                        "trionyx:model-list",
                        kwargs={
                            'app': model._meta.app_label,
                            'model': model._meta.model_name,
                        }
                    )
                )

    @classmethod
    def add_item(cls, path, name, icon=None, url=None, order=None, permission=None, active_regex=None):
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

        new_item = MenuItem(path, name, icon, url, order, permission, active_regex)

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
        if self.url and path.startswith(self.url):
            return True

        if self.active_regex and re.compile(self.active_regex).match(path):
            return True

        for child in self.childs:
            if child.is_active(path):
                return True
        return False


class Tab:
    _tabs = defaultdict(list)

    @classmethod
    def get_tabs(cls, model_alias, object):
        for item in cls._tabs[model_alias]:
            if item.display_filter(object):
                yield item

    @classmethod
    def get_tab(cls, model_alias, object, tab_code):
        for item in cls._tabs[model_alias]:
            if item.code == tab_code and item.display_filter(object):
                return item
        raise Exception('Given tab does not exits or is filtered')

    @classmethod
    def register(cls, model_alias, code='general', name=None, order=None, display_filter=None):
        """
        Register new tab

        :param model_alias:
        :param code:
        :param name:
        :param order:
        :return:
        """
        def wrapper(create_layout):
            item = TabItem(
                code=code,
                create_layout=create_layout,
                name=name,
                order=order,
                display_filter=display_filter
            )

            if item in cls._tabs[model_alias]:
                raise Exception("Tab {} already registered for model {}".format(code, model_alias))

            cls._tabs[model_alias].append(item)
            cls._tabs[model_alias] = sorted(cls._tabs[model_alias], key=lambda item: item.order if item.order else 999)

            return create_layout
        return wrapper

    @classmethod
    def register_update(cls, model_alias, code):
        def wrapper(update_layout):
            for item in cls._tabs[model_alias]:
                if item.code == code:
                    item.layout_updates.append(update_layout)
            return update_layout
        return wrapper

    @classmethod
    def update(cls, model_alias, code='general', name=None, order=None, display_filter=None):
        for item in cls._tabs[model_alias]:
            if item.code != code:
                continue
            if name:
                item.name = name
            if order:
                item.order = order
            if display_filter:
                item.display_filter = display_filter
            break
        cls._tabs[model_alias] = sorted(cls._tabs[model_alias], key=lambda item: item.code if item.code else 999)


class TabItem:

    def __init__(self, code, create_layout, name=None, order=None, display_filter=None):
        self.code = code
        self.create_layout = create_layout
        self.name = name
        self.order = order
        self.display_filter = display_filter if display_filter else lambda object: True
        self.layout_updates = []

    @property
    def name(self):
        if hasattr(self, '_name') and self._name:
            return self._name
        return self.code.replace('_', ' ').capitalize()

    @name.setter
    def name(self, name):
        self._name = name

    def get_layout(self, object):
        layout = self.create_layout(object)
        for update_layout in self.layout_updates:
            update_layout(layout, object)
        layout.set_object(object)
        return layout

    def __str__(self):
        if not self.name:
            return self.name.capitalize()
        return self.name

    def __eq__(self, other):
        return self.code == other.code
