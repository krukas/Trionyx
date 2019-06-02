"""
trionyx.config
~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import inspect

from django.apps import apps
from django.urls import reverse
from django.conf import settings

TX_MODEL_CONFIGS = settings.TX_CORE_MODEL_CONFIGS
TX_MODEL_CONFIGS.update(settings.TX_MODEL_CONFIGS)


class ModelConfig:
    """
    ModelConfig holds all config related to a model that is used for trionyx functionality.

    Model configs are auto loaded from the apps config file.
    In the apps config class create a class with same name as model and set appropriate config as class attribute.

    .. code-block:: python

        # apps.blog.apps.py
        class BlogConfig(BaseConfig):
            ...

            # Example config for Category model
            class Category:
                verbose_name = '{name}'
                list_default_fields = ['id', 'created_at', 'name']
                list_search_fields = ['name', 'description']

    """

    menu_name = None
    """Menu name, default is model verbose_name_plural"""

    menu_order = None
    """Menu order"""

    menu_exclude = False
    """Exclude model from menu"""

    menu_root = False
    """Add menu item to root instead of under the app menu"""

    menu_icon = None
    """Menu css icon, is ony used when root menu item"""

    global_search = True
    """Enable global search for model"""

    disable_search_index = False
    """Disable search index, use full for model with no list view but with allot of records"""

    search_fields = ()
    """Fields to use for searching, default is all CharField and TextField"""

    search_exclude_fields = ()
    """Fields you don't want to use for search"""

    search_title = None
    """
    Search title of model works the same as `verbose_name`, defaults to __str__.
    Is given high priority in search and is used in global search
    """

    search_description = None
    """
    Search description of model works the same as `verbose_name`, default is empty,
    Is given medium priority and is used in global search page
    """

    list_fields = None
    """
    Customise the available fields for model list view, default all model fields are available.

    list_fields is an array of dict with the field description, the following options are available:

    - **field**: Model field name (is used for sort and getting value if no renderer is supplied)
    - **label**: Column name in list view, if not set verbose_name of model field is used
    - **renderer**: function(model, field) that returns a JSON serializable date, when not set model field is used.

    .. code-block:: python

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
        """Init config"""
        self.model = model
        self.app_label = model._meta.app_label
        self.model_name = model._meta.model_name

        if MetaConfig:
            for key, value in MetaConfig.__dict__.items():
                if key.startswith('_'):
                    continue
                setattr(self, key, value)

    def __getattr__(self, item):
        """Get attribute and returns null if not set"""
        try:
            return super().__getattr__(item)
        except AttributeError:
            return None

    def get_fields(self, inlcude_base=False, include_id=False):
        """Get model fields"""
        for field in self.model._meta.fields:
            if field.name == 'deleted':
                continue
            if not include_id and field.name == 'id':
                continue
            if not inlcude_base and field.name in ['created_at', 'updated_at', 'created_by', 'verbose_name']:
                continue
            yield field

    def get_absolute_url(self, model):
        """Get model url"""
        return reverse('trionyx:model-view', kwargs={
            'app': model._meta.app_label,
            'model': model._meta.model_name,
            'pk': model.id
        })

    def get_list_fields(self):
        """Get all list fields"""
        from trionyx.renderer import renderer
        model_fields = {f.name: f for f in self.get_fields(True, True)}

        def create_list_fields(config_fields, list_fields=None):
            list_fields = list_fields if list_fields else {}

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
                    config['renderer'] = renderer.render_field

                if 'type' not in config and config['field'] in model_fields:
                    config['type'] = self.get_field_type(
                        self.model._meta.get_field(config['field'])
                    )

                if 'choices' not in config and config['field'] in model_fields:
                    config['choices'] = self.model._meta.get_field(config['field']).choices

                list_fields[config['field']] = config
            return list_fields

        list_fields = create_list_fields(model_fields.keys())

        if self.list_fields:
            list_fields = create_list_fields(self.list_fields, list_fields)

        return list_fields

    def get_field_type(self, field):
        """Get field type base on model field class"""
        from trionyx import models
        if isinstance(field, (models.CharField, models.TextField, models.EmailField)):
            return 'text'
        elif isinstance(field, (models.IntegerField, models.AutoField)):
            return 'int'
        elif isinstance(field, (models.DecimalField, models.FloatField)):
            return 'float'
        elif isinstance(field, models.BooleanField):
            return 'bool'
        elif isinstance(field, models.DateTimeField):
            return 'datetime'
        elif isinstance(field, models.DateField):
            return 'date'
        elif isinstance(field, (models.ForeignKey, models.OneToOneField)):
            return 'related'


class Models:
    """Holds all model configs"""

    def __init__(self):
        """Init models"""
        self.configs = {}

    def auto_load_configs(self):
        """Auto load all configs from app configs"""
        from trionyx.models import BaseModel

        for app in apps.get_app_configs():
            for model in app.get_models():
                config = ModelConfig(model, getattr(app, model.__name__, None))
                if not isinstance(config.model(), BaseModel):
                    config.disable_search_index = True
                self.configs[self.get_model_name(model)] = config

        # Update configs from settings
        for model_name, config in TX_MODEL_CONFIGS.items():
            for key, value in config.items():
                setattr(self.configs[model_name], key, value)

    def get_config(self, model):
        """Get config for given model"""
        if not inspect.isclass(model) and not isinstance(model, str):
            model = model.__class__
        return self.configs.get(self.get_model_name(model))

    def get_all_configs(self, trionyx_models_only=True):
        """Get all model configs"""
        from trionyx.models import BaseModel

        for index, config in self.configs.items():
            if trionyx_models_only and not isinstance(config.model(), BaseModel):
                continue

            yield config

    def get_model_name(self, model):
        """Get model name for given model"""
        if isinstance(model, str):
            return model
        return '{}.{}'.format(model._meta.app_label, model._meta.model_name)


models_config = Models()
