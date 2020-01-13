"""
trionyx.views
~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import logging
from collections import defaultdict

from django.utils.translation import ugettext_lazy as _
from trionyx.config import models_config, TX_MODEL_OVERWRITES
from trionyx.layout import Layout, Column12, Panel, DescriptionList, Component

from .models import (  # noqa F401
    ListView, ListJsendView, ListExportView, ListChoicesJsendView, DetailTabView,
    DetailTabJsendView, UpdateView, CreateView, DeleteView, LayoutView, LayoutUpdateView,
)
from .dialogs import (  # noqa F401
    DialogView, UpdateDialog, CreateDialog, LayoutDialog, DeleteDialog
)

from .ajax import JsendView  # noqa F401

logger = logging.getLogger(__name__)


class LayoutRegister:
    """Class where tab layout can be registered"""

    def __init__(self):
        """Init"""
        self.layouts = {}

    def add_layout(self, code, func):
        """Add layout"""
        if code in self.layouts and self.layouts[code]['layout']:
            raise Exception("Layout {} already registered".format(code))

        if code in self.layouts:
            self.layouts[code]['layout'] = func
        else:
            self.layouts[code] = {
                'layout': func,
                'updates': [],
            }

    def register(self, code):
        """Add layout to register"""
        def wrapper(create_layout):
            self.add_layout(code, create_layout)
            return create_layout
        return wrapper

    def add_layout_update(self, code, func):
        """Add update layout function"""
        if code in self.layouts:
            self.layouts[code]['updates'].append(func)
        else:
            self.layouts[code] = {
                'layout': False,
                'updates': [func],
            }

    def update(self, code):
        """Register an update for layout"""
        def wrapper(update_layout):
            self.add_layout_update(code, update_layout)
            return update_layout
        return wrapper

    def get_layout(self, code, object, layout_id=None):
        """Get complete layout for given object"""
        if code not in self.layouts:
            raise Exception('layout does not exist')

        layout_config = self.layouts.get(code)

        layout = layout_config['layout'](object)
        if isinstance(layout, Component):
            layout = Layout(layout)

        if isinstance(layout, list):
            layout = Layout(*layout)

        for update_layout in layout_config['updates']:
            try:
                update_layout(layout, object)
            except Exception as e:
                logger.error('Could not update layout for {}: {}'.format(
                    code,
                    str(e)
                ))

        from trionyx.urls import model_url

        if layout_id:
            layout.id = layout_id

        layout.update_url = model_url(object, 'layout-update', code=code)
        layout.set_object(object)

        return layout


class SidebarRegister:
    """Register sidebars"""

    def __init__(self):
        """Init"""
        self.sidebars = {}

    def register(self, model_alias, code=None):
        """Add sidebar to register

        The function must return a dict that can contain the following data:

        - **title**: Title of the sidebar
        - **content**: Html content to display in sidebar
        - **fixed_content (optional)**: Html content that is fixed displayed under the title
        - **theme (optional)**: Theme of sidebar can be light or dark
        - **hover (optional)**: Sidebar hovers over content instead of pushing it away
        - **actions (optional)**: List[Dict] of actions  that are displayed in dropdown.
            - **label**: Action label
            - **class**: class of action link
            - **url**: Url used for action link
            - **dialog** Action link url is an dialog
            - **dialog_options**: Dialog options
            - **reload**: On dialog success reload sidebar
            - **divider**: Add divider before action
        """
        model_alias = models_config.get_model_name(model_alias) if model_alias else ''

        if (model_alias, code) in self.sidebars:
            raise Exception(f'There is already a sidebar for model: {model_alias} and code: {code}')

        def wrapper(create_sidebar):
            self.sidebars[(model_alias, code)] = create_sidebar
            return create_sidebar

        return wrapper

    def get_sidebar(self, model_alias, code=None):
        """Get sidebar"""
        model_alias = models_config.get_model_name(model_alias) if model_alias else ''

        if (model_alias, code) not in self.sidebars:
            raise Exception(f'Sidebar does not exists for model: {model_alias} and code: {code}')

        return self.sidebars[(model_alias, code)]


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

    def register(self, model_alias, code='general', name=None, order=10, display_filter=None):
        """
        Register new tab

        :param model_alias:
        :param code:
        :param name:
        :param order:
        :return:
        """
        model_alias = self.get_model_alias(model_alias)

        if code == 'general' and not name:
            name = _('General')

        def wrapper(create_layout):
            item = TabItem(
                code=code,
                name=name,
                order=order,
                display_filter=display_filter,
                model_alias=model_alias
            )

            if item in self.tabs[model_alias]:
                raise Exception("Tab {} already registered for model {}".format(code, model_alias))

            self.tabs[model_alias].append(item)
            self.tabs[model_alias] = sorted(self.tabs[model_alias], key=lambda item: item.order if item.order else 10)
            layouts.add_layout(f'{model_alias}-{code}', create_layout)

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
            layouts.add_layout_update(f'{model_alias}-{code}', update_layout)
            return update_layout
        return wrapper

    def update(self, model_alias, code='general', name=None, order=10, display_filter=None):
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
        self.tabs[model_alias] = sorted(self.tabs[model_alias], key=lambda item: item.code if item.code else 10)

    def get_model_alias(self, model_alias):
        """Get model alias if class then convert to alias string"""
        name = models_config.get_model_name(model_alias)
        return TX_MODEL_OVERWRITES.get(name, name)

    def auto_generate_missing_tabs(self):
        """Auto generate tabs for models with no tabs"""
        for config in models_config.get_all_configs(False):
            model_alias = self.get_model_alias(config.model)
            if model_alias not in self.tabs:
                @self.register(model_alias, order=10)
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

    def __init__(self, code, name=None, order=None, display_filter=None, model_alias=None):
        """Init TabItem"""
        self._name = None
        self.code = code
        self.name = name
        self.order = order
        self.display_filter = display_filter if display_filter else lambda object: True
        self.model_alias = model_alias

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
        model_alias = self.model_alias if self.model_alias else tabs.get_model_alias(object)
        return layouts.get_layout(f'{model_alias}-{self.code}', object)

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
sidebars = SidebarRegister()
