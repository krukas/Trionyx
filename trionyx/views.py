"""
trionyx.views
~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
from trionyx.routers import AutoRouter


class ModelView:
    """Class for registering model views"""

    _views = {}

    LIST = 'list'
    VIEW = 'view'
    ADD = 'add'
    EDIT = 'edit'
    DELETE = 'delete'

    @staticmethod
    def get_model_id(model):
        """Get model id based on model class"""
        return '{}_{}'.format(model._meta.app_label, model.__name__).lower()

    @classmethod
    def set_model_view(cls, model, layout, view=VIEW, alias=None):
        """
        Set model view

        You can use alias to create more views for the same model

        :param model: Model class
        :param layout: Widget Node structure
        :param view: View mode
        :param alias: An alias for model
        :return:
        """
        if alias:
            model_id = alias
        else:
            model_id = cls.get_model_id(model)

        if model_id not in cls._views:
            cls._views[model_id] = {
                'model_id': model_id,
                'model_url': AutoRouter.get_model_prefix(model),
                'views': {}
            }

        cls._views[model_id]['views'][view] = layout

    @classmethod
    def set_default_model_views(cls, model):
        """
        Set default model views for given model

        :param model: Model class
        :return:
        """
        from trionyx.widgets import layout
        from trionyx.widgets import widgets

        # Add Default list view
        cls.set_model_view(
            model,
            layout.EmptyLayout(
                children=widgets.ListTable(
                    fields=list(model.get_model_fields(False))
                )
            ),
            cls.LIST)

        cls.set_model_view(
            model,
            layout.EmptyLayout(
                children=widgets.Form(
                    fields=list(model.get_model_fields())
                )
            ),
            cls.ADD)

        cls.set_model_view(
            model,
            layout.EmptyLayout(
                children=widgets.Form(
                    fields=list(model.get_model_fields())
                )
            ),
            cls.EDIT)

        cls.set_model_view(
            model,
            layout.EmptyLayout(
                children=widgets.DataTable(
                    fields=list(model.get_model_fields())
                )
            ),
            cls.VIEW)

    @classmethod
    def get_config(cls):
        """
        Return model views config

        :return: Model views
        """
        items = []

        for _, data in cls._views.items():
            item = {
                'model_id': data['model_id'],
                'model_url': data['model_url'],
                'views': {}
            }

            for view_id, layout in data['views'].items():
                item['views'][view_id] = layout.to_config()

            items.append(item)
        return items
