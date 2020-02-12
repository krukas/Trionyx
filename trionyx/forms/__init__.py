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
from typing import List, Optional, Dict

from django.forms import *  # noqa F403
from django.forms import ModelForm as DjangoModelForm
from django.db.models.fields import NOT_PROVIDED
from django.db import transaction
from django.conf import settings
from django.urls import reverse

from trionyx.config import models_config
from trionyx import utils

logger = logging.getLogger(__name__)

TX_MODEL_OVERWRITES_REVERSE = {value.lower(): key.lower() for key, value in settings.TX_MODEL_OVERWRITES.items()}


class ModelAjaxChoiceField(ModelChoiceField):
    """
    Ajax model choice field, for Trionyx models.

    Note: This will not work if this is used with a form that is displayed multiple times on a page.
    """

    registered_fields: Dict[str, ModelChoiceField] = {}

    def __init__(self, queryset, *args, **kwargs):
        """Init"""
        self.field_id = utils.random_string(16)
        self.registered_fields[self.field_id] = self
        super().__init__(queryset, *args, **kwargs)

    @property
    def choices(self):
        """Get active choices"""
        from django.utils.functional import lazy
        # Lazy function is used, because first call to choices if before `prepare_value`
        return lazy(self.lazy_choices, list)()

    def lazy_choices(self):
        """Lazy choices, is used to get active choices"""
        from trionyx.trionyx import LOCAL_DATA
        value = getattr(LOCAL_DATA, f'choices-{self.field_id}', None)
        return self.queryset.filter(id=value).values_list('id', 'verbose_name') if value else []

    def prepare_value(self, value):
        """Prepare value and store value in local data"""
        from trionyx.trionyx import LOCAL_DATA
        setattr(LOCAL_DATA, f'choices-{self.field_id}', value)
        return super().prepare_value(value)

    def widget_attrs(self, widget):
        """Set select2 widget data"""
        return {
            'data-ajax-url': reverse('trionyx:form-choices', kwargs={'id': self.field_id}),
        }


class ModelAjaxMultipleChoiceField(ModelMultipleChoiceField):
    """
    Ajax model multiple choice field, for Trionyx models.

    Note: This will not work if this is used with a form that is displayed multiple times on a page.
    """

    def __init__(self, queryset, *args, **kwargs):
        """Init"""
        self.field_id = utils.random_string(16)
        ModelAjaxChoiceField.registered_fields[self.field_id] = self
        super().__init__(queryset, *args, **kwargs)

    @property
    def choices(self):
        """Get active choices"""
        from django.utils.functional import lazy
        return lazy(self.lazy_choices, list)()

    def lazy_choices(self):
        """Get active choices"""
        from trionyx.trionyx import LOCAL_DATA
        values = getattr(LOCAL_DATA, f'choices-{self.field_id}', None)
        return [(v.id, v.verbose_name) for v in values] if values else []

    def prepare_value(self, value):
        """Prepare value"""
        from trionyx.trionyx import LOCAL_DATA
        setattr(LOCAL_DATA, f'choices-{self.field_id}', value)
        return super().prepare_value(value)

    def widget_attrs(self, widget):
        """Set select2 widget data"""
        return {
            'data-ajax-url': reverse('trionyx:form-choices', kwargs={'id': self.field_id}),
        }


class ModelForm(DjangoModelForm):  # type: ignore
    """Trionyx ModelForm"""

    css_files: List[str] = []
    """CSS files that need to be loaded"""

    js_files: List[str] = []
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

                if 'queryset' in options:
                    self.__inline_forms[key] = options['form'](
                        self.data if self.data else None,
                        queryset=options['queryset'],
                        **kwargs
                    )
                else:
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


class Wysiwyg(CharField):
    """Wysiwyg summernote form field"""

    def __init__(self, *args, **kwargs):
        """Init field"""
        if not kwargs.get('widget'):
            kwargs['widget'] = Textarea(attrs={'class': 'summernote'})
        super().__init__(*args, **kwargs)


class FormRegister:
    """Class where forms can be registered"""

    def __init__(self):
        """Init"""
        self.forms = defaultdict(dict)

    def register(
        self, code: Optional[str] = None, model_alias: Optional[str] = None,
        default_create: Optional[bool] = False, default_edit: Optional[bool] = False, minimal: Optional[bool] = False
    ):
        """Register form for given model_alias,
        if no model_alias is given the Meta.model is used to generate the model alias.

        :param str code: Code to identify form
        :param str model_alias: Alias for a model (if not provided the Meta.model is used)
        :param bool default_create: Use this form for create
        :param bool default_edit: Use this form for editing
        :param bool minimal: Use this form for minimal create

        .. code-block:: python

            # <app>/forms.py
            from trionyx import forms

            @forms.register(default_create=True, default_edit=True)
            class UserForm(forms.ModelForm):

                class Meta:
                    model = User

        """
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
register = form_register.register
