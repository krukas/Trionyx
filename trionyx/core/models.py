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

    def get_queryset(self):
        """Give qeuryset where deleted items are filtered"""
        return super().get_queryset().filter(deleted=False)
        

class BaseModel(models.Model):
    """Base model for all Trionyx models"""

    objects = BaseManager()

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
        # TODO: get from model config 
        return self.verbose_name.format(model_name=model_name, app_label=app_label, **self.__dict__)
