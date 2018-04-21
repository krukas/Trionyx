"""
trionyx.navigation
~~~~~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import re
import inspect
from collections import defaultdict

from django.apps import apps
from django.urls import reverse

from trionyx.config import models_config
from trionyx.layout import Layout, Column12, Panel, DescriptionList, Component


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
                    )
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

    def get_menu_items(self):
        """Get menu items"""
        if not self.root_item:
            return []
        return self.root_item.childs


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


class TabRegister:
    """Class where tab layout can be registered"""

    def __init__(self):
        """Init Tabs"""
        self.tabs = defaultdict(list)

    def get_tabs(self, model_alias, object):
        """
        Get all active tabs for given model

        :param model_alias:
        :param object: Object used to filter tabs
        :return:
        """
        model_alias = self.get_model_alias(model_alias)
        for item in self.tabs[model_alias]:
            if item.display_filter(object):
                yield item

    def get_tab(self, model_alias, object, tab_code):
        """
        Get tab for given object and tab code

        :param model_alias:
        :param object: Object used to render tab
        :param tab_code: Tab code to use
        :return:
        """
        model_alias = self.get_model_alias(model_alias)
        for item in self.tabs[model_alias]:
            if item.code == tab_code and item.display_filter(object):
                return item
        raise Exception('Given tab does not exits or is filtered')

    def register(self, model_alias, code='general', name=None, order=None, display_filter=None):
        """
        Register new tab

        :param model_alias:
        :param code:
        :param name:
        :param order:
        :return:
        """
        model_alias = self.get_model_alias(model_alias)

        def wrapper(create_layout):
            item = TabItem(
                code=code,
                create_layout=create_layout,
                name=name,
                order=order,
                display_filter=display_filter
            )

            if item in self.tabs[model_alias]:
                raise Exception("Tab {} already registered for model {}".format(code, model_alias))

            self.tabs[model_alias].append(item)
            self.tabs[model_alias] = sorted(self.tabs[model_alias], key=lambda item: item.order if item.order else 999)

            return create_layout
        return wrapper

    def register_update(self, model_alias, code):
        """
        Register tab update function, function is being called with (layout, object)

        :param model_alias:
        :param code:
        :return:
        """
        model_alias = self.get_model_alias(model_alias)

        def wrapper(update_layout):
            for item in self.tabs[model_alias]:
                if item.code == code:
                    item.layout_updates.append(update_layout)
            return update_layout
        return wrapper

    def update(self, model_alias, code='general', name=None, order=None, display_filter=None):
        """
        Update given tab

        :param model_alias:
        :param code:
        :param name:
        :param order:
        :param display_filter:
        :return:
        """
        model_alias = self.get_model_alias(model_alias)
        for item in self.tabs[model_alias]:
            if item.code != code:
                continue
            if name:
                item.name = name
            if order:
                item.order = order
            if display_filter:
                item.display_filter = display_filter
            break
        self.tabs[model_alias] = sorted(self.tabs[model_alias], key=lambda item: item.code if item.code else 999)

    def get_model_alias(self, model_alias):
        """Get model alias if class then convert to alias string"""
        from trionyx.models import BaseModel
        if inspect.isclass(model_alias) and issubclass(model_alias, BaseModel):
            config = models_config.get_config(model_alias)
            return '{}.{}'.format(config.app_label, config.model_name)
        return model_alias

    def auto_generate_missing_tabs(self):
        """Auto generate tabs for models with no tabs"""
        for config in models_config.get_all_configs():
            model_alias = '{}.{}'.format(config.app_label, config.model_name)
            if model_alias not in self.tabs:
                @self.register(model_alias)
                def general_layout(obj):
                    return Layout(
                        Column12(
                            Panel(
                                'info',
                                DescriptionList(*[f.name for f in obj.get_fields()])
                            )
                        )
                    )


class TabItem:
    """Tab item that holds the tab data and renders the layout"""

    def __init__(self, code, create_layout, name=None, order=None, display_filter=None):
        """Init TabItem"""
        self._name = None
        self.code = code
        self.create_layout = create_layout
        self.name = name
        self.order = order
        self.display_filter = display_filter if display_filter else lambda object: True
        self.layout_updates = []

    @property
    def name(self):
        """Give back tab name if is set else generate name by code"""
        if self._name:
            return self._name
        return self.code.replace('_', ' ').capitalize()

    @name.setter
    def name(self, name):
        """Set name"""
        self._name = name

    def get_layout(self, object):
        """Get complete layout for given object"""
        layout = self.create_layout(object)
        if isinstance(layout, Component):
            layout = Layout(layout)

        if isinstance(layout, list):
            layout = Layout(*layout)

        for update_layout in self.layout_updates:
            update_layout(layout, object)
        layout.set_object(object)
        return layout

    def __str__(self):
        """Tab string representation"""
        if not self.name:
            return self.name.capitalize()
        return self.name

    def __eq__(self, other):
        """Compare tab based on code"""
        return self.code == other.code


tabs = TabRegister()
app_menu = Menu()
