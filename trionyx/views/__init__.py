"""
trionyx.views
~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import inspect
from collections import defaultdict

from trionyx.config import models_config
from trionyx.layout import Layout, Column12, Panel, DescriptionList, Component

from .models import (  # noqa F401
    ListView, ListJsendView, ListExportView, ListChoicesJsendView, DetailTabView,
    DetailTabJsendView, UpdateView, CreateView, DeleteView, LayoutView,
)
from .dialogs import (  # noqa F401
    DialogView, UpdateDialog, CreateDialog, LayoutDialog, DeleteDialog
)


class LayoutRegister:
    """Class where tab layout can be registered"""

    def __init__(self):
        """Init"""
        self.layouts = {}

    def register(self, code):
        """Add layout to register"""
        def wrapper(create_layout):
            self.layouts[code] = create_layout
            return create_layout
        return wrapper

    def get_layout(self, code, object, request=None):
        """Get complete layout for given object"""
        if code not in self.layouts:
            raise Exception('layout does not exist')
        layout = self.layouts.get(code)
        layout = layout(object)
        if isinstance(layout, Component):
            layout = Layout(layout)

        if isinstance(layout, list):
            layout = Layout(*layout)

        layout.set_object(object)
        return layout.render(request)


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

        for item in self.tabs.get(model_alias, list()):
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
        for config in models_config.get_all_configs(False):
            model_alias = '{}.{}'.format(config.app_label, config.model_name)
            if model_alias not in self.tabs:
                @self.register(model_alias)
                def general_layout(obj):
                    return Layout(
                        Column12(
                            Panel(
                                'info',
                                DescriptionList(*[f.name for f in models_config.get_config(obj).get_fields()])
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
layouts = LayoutRegister()
