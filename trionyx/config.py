import inspect
from datetime import datetime

from django.apps import apps
from django.forms.models import modelform_factory
from django.db.models import NOT_PROVIDED
from django.utils import formats

from trionyx.utils import import_object_by_string


class ModelConfig:
    """
    ModelConfig holds all config related to a model that is used for trionyx functionality.

    Model configs are auto loaded from the apps config file.
    In the apps config class create a class with same name as model and set appropriate config as class attribute.

    .. code-block: python

        class BlogConfig(BaseConfig):
            ...

            # Example config for Category model
            class Category:
                verbose_name = '{name}'
                list_default_fields = ['id', 'created_at', 'name']
                list_search_fields = ['name', 'description']

    """

    create_form = None
    """
    String of form class that is used for create, default will create form based on model. 
    Form is rendered with crispy forms
    """

    create_form_minimal = None
    """
    String of form class that is used for minimal create, default is form with all required fields. 
    Form is rendered with crispy forms.
    """

    edit_form = None
    """
    String of form class that is used for edit, default will create form based on model. 
    Form is rendered with crispy forms.
    """

    list_fields = None
    """
    Customise the available fields for model list view, default all model fields are available.
    
    list_fields is an array of dict with the field description, the following options are available:
    
    - **field**: Model field name (is used for sort and getting value if no renderer is supplied)
    - **label**: Column name in list view, if not set verbose_name of model field is used
    - **renderer**: function(model, field) that returns a JSON serializable date, when not set model field is used.
    
    .. code-block: python
    
         list_fields = [
            {
                'field': 'first_name',
                'label': 'Real first name',
                'renderer': lambda model field: model.first_name.upper()
            }
         ]
    """

    list_default_fields = None
    """Array of fields that default is used in form list"""

    list_search_fields = None
    """Array of fields to use with search can also be foreignkey relation like user__first_name"""

    list_select_related = None
    """Array of fields to add foreign-key relationships to query, use this for relations that are used in search or renderer"""

    verbose_name = "{model_name}({id})"
    """
    Verbose name used for displaying model, default value is "{model_name}({id})"

    format can be used to get model attributes value, there are two extra values supplied:
        - app_label: App name
        - model_name: Class name of model
    """

    def __init__(self, model, MetaConfig=None):
        self.model = model

        if MetaConfig:
            for key, value in MetaConfig.__dict__.items():
                if key.startswith('_'):
                    continue
                setattr(self, key, value)

    def __getattr__(self, item):
        try:
            return super().__getattr__(item)
        except:
            return None

    def get_create_form(self):
        return self._get_form('create_form')

    def get_create_minimal_form(self):
        return self._get_form('create_form_minimal', True)

    def get_edit_form(self):
        return self._get_form('edit_form')

    def get_list_fields(self):
        model_fields = {f.name: f for f in self.model.get_fields(True, True)}

        def create_list_fields(config_fields, list_fields=None):
            list_fields = list_fields if list_fields else {}

            def default_renderer(model, field):
                value = getattr(model, field, '')

                if isinstance(value, datetime):
                    value = formats.date_format(value, "SHORT_DATETIME_FORMAT")
                return value

            for field in config_fields:
                config = field
                if isinstance(field, str):
                    config = {'field': field}

                if 'field' not in config:
                    raise Exception("Field config is missing field: {}".format(config))
                if 'label' not in config:
                    if config['field'] in model_fields:
                        config['label'] = model_fields[config['field']].verbose_name
                    else:
                        config['label'] = config['field']
                if 'renderer' not in config:
                    config['renderer'] = default_renderer

                list_fields[config['field']] = config
            return list_fields

        list_fields = create_list_fields(model_fields.keys())

        if self.list_fields:
            list_fields = create_list_fields(self.list_fields, list_fields)

        return list_fields

    def _get_form(self, config_name, only_required=False):
        if getattr(self, config_name, None):
            return import_object_by_string(getattr(self, config_name))

        def use_field(field):
            if not only_required:
                return True
            return field.default == NOT_PROVIDED

        return modelform_factory(self.model, fields=[f.name for f in self.model.get_fields() if use_field(f)])

class Models:

    def __init__(self):
        self.configs = {}

    def auto_load_configs(self):
        for app in apps.get_app_configs():
            for model in app.get_models():
                config = ModelConfig(model, getattr(app, model.__name__, None))
                self.configs[self.get_model_name(model)] = config

    def get_config(self, model):
        if not inspect.isclass(model):
            model = model.__class__
        return self.configs.get(self.get_model_name(model))

    def get_model_name(self, model):
        return '{}.{}'.format(model.__module__, model.__name__)


models_config = Models()