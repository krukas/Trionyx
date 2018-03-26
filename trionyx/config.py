import inspect

from django.apps import apps
from django.forms.models import modelform_factory
from django.db.models import NOT_PROVIDED

from trionyx.utils import import_object_by_string


class ModelConfig:
    create_form = None
    create_form_minimal = None
    edit_form = None

    verbose_name = "{model_name}({id})"

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