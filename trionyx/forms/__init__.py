"""
trionyx.forms
~~~~~~~~~~~~~

Core forms for Trionyx

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import logging
import inspect
from collections import defaultdict

from django.forms import *  # noqa F403
from django.forms import ModelForm as DjangoModelForm
from django.db.models import NOT_PROVIDED
from django.db import transaction
from django.conf import settings

from trionyx.config import models_config

logger = logging.getLogger(__name__)

TX_MODEL_OVERWRITES_REVERSE = {value.lower(): key.lower() for key, value in settings.TX_MODEL_OVERWRITES.items()}


class ModelForm(DjangoModelForm):
    """Trionyx ModelForm"""

    css_files = []
    """CSS files that need to be loaded"""

    js_files = []
    """JS files that need to be loaded"""

    def get_inline_forms(self):
        """Get inline forms"""
        if not hasattr(self, '__inline_forms'):
            self.__inline_forms = {}
            for key, options in getattr(self, 'inline_forms', {}).items():
                kwargs = {
                    'prefix': key,
                }

                fk_name = options.get('fk_name', 'instance')
                if fk_name == 'instance':
                    kwargs['instance'] = self.instance
                else:
                    kwargs['instance'] = getattr(self.instance, key, None)
                    kwargs['initial'] = {
                        fk_name: self.instance
                    }

                self.__inline_forms[key] = options['form'](self.data if self.data else None, **kwargs)

        return self.__inline_forms

    def is_valid(self):
        """Check if form and inline forms are valid"""
        valid = super().is_valid()

        for key, form in self.get_inline_forms().items():
            valid = valid and form.is_valid()

        return valid

    def save(self, commit=True):
        """Save form and inline forms"""
        object_updated = False
        config = models_config.get_config(self._meta.model)
        fields = [field.name for field in config.get_fields()]
        with transaction.atomic():
            obj = super().save(commit)

            for key, form in self.get_inline_forms().items():
                form.is_valid()  # Make sure cleaned_data is filled
                fk_name = self.inline_forms[key].get('fk_name', 'instance')
                if fk_name == 'instance':
                    logger.debug('Save inline form {} as FormSet, commit: {}'.format(key, commit))
                    form.instance = obj
                    form.save(commit)
                else:
                    logger.debug('Save inline form {} as Form, commit: {}'.format(key, commit))
                    inline_obj = form.save(False)
                    if inline_obj:
                        setattr(inline_obj, fk_name, obj)
                        if commit:
                            inline_obj.save()

                        if key in fields:
                            logger.debug(' * Set inline form object on parent form as: {}'.format(key))
                            setattr(obj, key, inline_obj)
                            object_updated = True

        if object_updated and commit:
            obj.save()
        return obj


class FormRegister:
    """Class where forms can be registered"""

    def __init__(self):
        """Init"""
        self.forms = defaultdict(dict)

    def add_form(self, code=None, model_alias=None, default_create=False, default_edit=False, minimal=False):
        """Add form to register"""
        def wrapper(form):
            form_code = code if code else form.__name__.lower()
            model_name = self.get_model_alias(model_alias if model_alias else form.Meta.model, False)

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

    def get_model_alias(self, model_alias, rewrite=True):
        """Get model alias if class then convert to alias string"""
        from trionyx.models import Model
        if inspect.isclass(model_alias) and issubclass(model_alias, Model):
            if rewrite:
                models_config.get_model_name(models_config.get_config(model_alias).model)
            return models_config.get_model_name(model_alias)
        return model_alias

    def get_form(self, model, code):
        """Get form based on code"""
        return self.forms.get(self.get_model_alias(model), dict()).get(code)['form']

    def get_all_forms(self, model):
        """Get all forms for model"""
        return [config['form'] for code, config in self.forms.get(self.get_model_alias(model), dict()).items()]

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

        # Check for original form
        if model_alias in TX_MODEL_OVERWRITES_REVERSE:
            model_alias = TX_MODEL_OVERWRITES_REVERSE.get(model_alias)
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
