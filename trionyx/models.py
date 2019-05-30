"""
trionyx.models
~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from django.db.models import *  # noqa F403
from django.urls import reverse
from jsonfield import JSONField  # noqa F401

from trionyx.config import models_config


# =============================================================================
# Fields
# =============================================================================
class PriceField(DecimalField):  # noqa F405
    """Price field is Decimal(11,4) field, has no extra logic only for rendering"""

    def __init__(self, *args, **kwargs):
        """Init PriceField"""
        kwargs['max_digits'] = 11
        kwargs['decimal_places'] = 4
        super().__init__(*args, **kwargs)


# =============================================================================
# Base models
# =============================================================================
class BaseManager(Manager):  # noqa F405
    """model base manager for all Trionyx models"""

    def get_queryset(self):
        """Give qeuryset where deleted items are filtered"""
        return super().get_queryset().filter(deleted=False)


class BaseModel(Model):  # noqa F405
    """Base model for all Trionyx models"""

    objects = BaseManager()

    created_at = DateTimeField(auto_now_add=True)  # noqa F405
    """Created at field, date is set when model is created"""

    updated_at = DateTimeField(auto_now=True)  # noqa F405
    """Update at field, date is set when model is saved"""

    deleted = BooleanField(default=False)  # noqa F405
    """Deleted field, object is soft deleted"""

    class Meta:
        """Meta information for BaseModel"""

        abstract = True
        default_permissions = ('read', 'add', 'change', 'delete')

    @classmethod
    def get_fields(cls, inlcude_base=False, include_id=False):
        """Get model fields"""
        for field in cls._meta.fields:
            if field.name == 'deleted':
                continue
            if not include_id and field.name == 'id':
                continue
            if not inlcude_base and field.name in ['created_at', 'updated_at']:
                continue
            yield field

    def __str__(self):
        """Give verbose name of object"""
        from trionyx.renderer import LazyFieldRenderer
        app_label = self._meta.app_label
        model_name = type(self).__name__
        verbose_name = models_config.get_config(self).verbose_name
        return verbose_name.format(model_name=model_name, app_label=app_label, **{
            field.name: LazyFieldRenderer(self, field.name)
            for field in self.get_fields(True, True)
        })

    def get_absolute_url(self):
        """Get model url"""
        return reverse('trionyx:model-view', kwargs={
            'app': self._meta.app_label,
            'model': self._meta.model_name,
            'pk': self.id
        })
