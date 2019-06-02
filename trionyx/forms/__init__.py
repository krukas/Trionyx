"""
trionyx.forms
~~~~~~~~~~~~~

Core forms for Trionyx

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import inspect
from collections import defaultdict

from django.forms import *  # noqa F403
from django.db.models import NOT_PROVIDED

from trionyx.config import models_config


class FormRegister:
    """Class where forms can be registered"""

    def __init__(self):
        """Init"""
        self.forms = defaultdict(dict)

    def add_form(self, code=None, model_alias=None, default_create=False, default_edit=False, minimal=False):
        """Add form to register"""
        def wrapper(form):
            form_code = code if code else form.__name__.lower()
            model_name = self.get_model_alias(model_alias if model_alias else form.Meta.model)

            if form_code in self.forms[model_name]:
                raise Exception("Form {} already registered for model {}".format(code, model_name))

            self.forms[model_name][form_code] = {
                'form': form,
                'default_create': default_create,
                'default_edit': default_edit,
                'minimal': minimal,
            }
            return form

        return wrapper

    def get_model_alias(self, model_alias):
        """Get model alias if class then convert to alias string"""
        from trionyx.models import BaseModel
        if inspect.isclass(model_alias) and issubclass(model_alias, BaseModel):
            config = models_config.get_config(model_alias)
            return '{}.{}'.format(config.app_label, config.model_name)
        return model_alias

    def get_form(self, model, code):
        """Get form based on code"""
        return self.forms.get(self.get_model_alias(model), dict()).get(code)['form']

    def get_create_form(self, model):
        """Get default create form"""
        form = self._get_model_form_by_config(model, 'default_create')
        return form if form else self._create_form(model)

    def get_create_minimal_form(self, model):
        """Get default minimal create form"""
        form = self._get_model_form_by_config(model, 'minimal')
        return form if form else self._create_form(model, True)

    def get_edit_form(self, model):
        """Get default edit form"""
        form = self._get_model_form_by_config(model, 'default_edit')
        return form if form else self._create_form(model)

    def _get_model_form_by_config(self, model, config):
        """Get default form"""
        model_alias = self.get_model_alias(model)
        for _, form in self.forms.get(model_alias, dict()).items():
            if form[config]:
                return form['form']
        return None

    def _create_form(self, model, only_required=False):
        """Create form from model"""
        def use_field(field):
            if not only_required:
                return True
            return field.default == NOT_PROVIDED

        config = models_config.get_config(model)
        return modelform_factory(model, fields=[f.name for f in config.get_fields() if use_field(f)])


form_register = FormRegister()
register = form_register.add_form
