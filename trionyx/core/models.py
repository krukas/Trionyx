"""
trionyx.core.models
~~~~~~~~~~~~~~~~

Core models

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import django
from django.db import models


class BaseManager(models.Manager):
    """model base manager for all Trionyx models"""

    ignore_models = [
        'django.contrib.auth.models.Permission',
        'django.contrib.sessions.models.Session',
        'django.contrib.contenttypes.models.ContentType',
        'django.contrib.admin.models.LogEntry',
        'rest_framework.authtoken.models.Token',
    ]
    """List of models that can be ignored by Trionyx"""

    def get_queryset(self):
        """Give qeuryset where deleted items are filtered"""
        return super().get_queryset().filter(deleted=False)

    @classmethod
    def add_ignore_model(cls, model):
        """Add an model to the ignore list"""
        cls.ignore_models.append(model)

    @classmethod
    def get_model_definitions(cls):
        """Get all model definitions"""
        return

    @classmethod
    def get_all_models(cls, remove_ignore=True, remove_no_api=True):
        """
        Get all active models

        :param remove_ignore: Removes models from ignore list
        :param remove_no_api: Remove models with NO_API=True
        :return:
        """
        for model in django.apps.apps.get_models():
            if cls.is_active_model(model, remove_ignore, remove_no_api):
                yield model

    @classmethod
    def is_active_model(cls, model, check_ignore=True, check_no_api=True):
        """
        Check if model is an active Trionyx model

        :param model: Model class
        :param check_ignore:
        :param check_no_api:
        :return:
        """
        if not model:
            return False

        print(model)
        print(isinstance(model(), BaseModel))

        full_class_name = '{}.{}'.format(model.__module__, model.__name__)
        if check_ignore and full_class_name in cls.ignore_models:
            return False

        if check_no_api and hasattr(model, 'NO_API') and getattr(model, 'NO_API'):
            return False

        return True


class AbstractModelBase(models.base.ModelBase):
    """Metaclass for Basemodel"""

    def __new__(cls, name, bases, attrs):
        """On new class creation set default model views"""
        new = super().__new__(cls, name, bases, attrs)

        if not (hasattr(new._meta, 'abstract') and new._meta.abstract):
            from trionyx.views import ModelView
            ModelView.set_default_model_views(new)

        return new


class BaseModel(models.Model, metaclass=AbstractModelBase):
    """Base model for all Trionyx models"""

    objects = BaseManager()

    verbose_name = "{model_name}: {id}"
    """
    Verbose name used for displaying model

    format can be used to get model attributes value, there are two extra values supplied:
        - app_label: App name
        - model_name: Class name of model
    """

    search_fields = []
    """
    Field that can be used to search model

    Can set a search weight by appending :<weight> to field, example: title:7
    """

    created_at = models.DateTimeField(auto_now_add=True)
    """Created at field, date is set when model is created"""

    updated_at = models.DateTimeField(auto_now=True)
    """Update at field, date is set when model is saved"""

    deleted = models.BooleanField(default=False)
    """Deleted field, object is soft deleted"""

    class Meta:
        """Meta information for BaseModel"""

        abstract = True
        default_permissions = ('read', 'add', 'change', 'delete')

    def __str__(self):
        """Give verbose name of object"""
        app_label = self._meta.app_label
        model_name = type(self).__name__
        return self.verbose_name.format(model_name=model_name, app_label=app_label, **self.to_dict())

    @classmethod
    def get_model_fields(self, remove_id=True):
        """Get all the model fields excluding the id field"""
        for field in self._meta.fields:
            if remove_id and field.name == 'id':
                continue
            yield field.name

    def to_dict(self):
        """Give dict with all model attributes values"""
        opts = self._meta
        data = {}
        for f in opts.concrete_fields + opts.many_to_many:
            if isinstance(f, models.ManyToManyField):
                if self.pk is None:
                    data[f.name] = []
                else:
                    data[f.name] = list(f.value_from_object(self).values_list('pk', flat=True))
            else:
                data[f.name] = f.value_from_object(self)
        return data
