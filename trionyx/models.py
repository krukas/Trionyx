"""
trionyx.models
~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import operator
from collections import defaultdict
from functools import reduce

from django.conf import settings
from django.db.models import *  # noqa F403
from jsonfield import JSONField  # type: ignore # noqa F401
from django.urls import reverse

from django.contrib import messages
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from trionyx.config import models_config
from trionyx import utils


TX_MODEL_OVERWRITES = {key.lower(): value.lower() for key, value in settings.TX_MODEL_OVERWRITES.items()}


def get_name(model):
    """Get model name"""
    name = models_config.get_model_name(model)
    return TX_MODEL_OVERWRITES.get(name, name)


def get_class(model):
    """Get model class"""
    return models_config.get_config(get_name(model)).model


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
class BaseManager(Manager):  # type: ignore # noqa F405
    """model base manager for all Trionyx models"""

    def get_queryset(self):
        """Give qeuryset where deleted items are filtered"""
        return super().get_queryset().filter(deleted=False)


class BaseModel(Model):  # noqa F405
    """Base model for all Trionyx models"""

    objects = BaseManager()  # type: ignore

    created_at = DateTimeField(_('Created at'), auto_now_add=True)  # noqa F405
    """Created at field, date is set when model is created"""

    updated_at = DateTimeField(_('Updated at'), auto_now=True)  # noqa F405
    """Update at field, date is set when model is saved"""

    deleted = BooleanField(_('Deleted'), default=False)  # noqa F405
    """Deleted field, object is soft deleted"""

    created_by = ForeignKey(
        get_name('trionyx.User'), SET_NULL, default=None, blank=True, null=True,
        related_name='+', verbose_name=_('Created by'))
    """Created by field"""

    verbose_name = TextField(_('Verbose name'), default='', blank=True)
    """Verbose name field"""

    class Meta:
        """Meta information for BaseModel"""

        abstract = True

    def __str__(self):
        """Give verbose name of object"""
        return self.verbose_name if self.verbose_name else self.generate_verbose_name()

    def save(self, *args, **kwargs):
        """Save model"""
        try:
            self.verbose_name = self.generate_verbose_name()
        except Exception:
            pass

        try:
            if not self.pk and not self.created_by:
                self.created_by = utils.get_current_request().user
        except Exception:
            pass

        return super().save(*args, **kwargs)

    def generate_verbose_name(self):
        """Generate verbose name"""
        from trionyx.renderer import LazyFieldRenderer
        app_label = self._meta.app_label
        model_name = type(self).__name__
        verbose_name = models_config.get_config(self).verbose_name
        return verbose_name.format(model_name=model_name, app_label=app_label, **{
            field.name: LazyFieldRenderer(self, field.name, no_html=True)
            for field in models_config.get_config(self).get_fields(True, True)
        })

    def get_absolute_url(self):
        """Get model url"""
        return reverse('trionyx:model-view', kwargs={
            'app': self._meta.app_label,
            'model': self._meta.model_name,
            'pk': self.id
        })


def filter_queryset_with_user_filters(queryset, filters, request=None):
    """Apply user provided filters on queryset"""
    config = models_config.get_config(queryset.model)

    field_indexed = {
        name: {
            'name': name,
            'label': field['label'],
            'type': field['type'],
            'choices': field['choices'],
        }
        for name, field in config.get_list_fields().items()
    }
    grouped_filter = defaultdict(list)
    for filter in filters:
        field = field_indexed.get(filter['field'])

        if not field:
            continue

        try:
            if filter['operator'] == 'null':
                queryset = queryset.filter(**{'{}__isnull'.format(filter['field']): filter['value']})
            elif field['type'] == 'datetime':
                filter['value'] = timezone.make_aware(
                    timezone.datetime.strptime(filter['value'], utils.get_datetime_input_format()))
            elif field['type'] == 'date':
                filter['value'] = timezone.make_aware(timezone.datetime.strptime(
                    filter['value'],
                    utils.get_datetime_input_format(date_only=True)))

            if filter['operator'] == '==':
                grouped_filter[filter['field']].append(filter['value'])
            elif filter['operator'] == '!=':
                if field['type'] == 'text':
                    queryset = queryset.exclude(**{'{}__icontains'.format(filter['field']): filter['value']})
                else:
                    queryset = queryset.exclude(**{filter['field']: filter['value']})
            elif filter['operator'] == '<':
                queryset = queryset.filter(**{'{}__lt'.format(filter['field']): filter['value']})
            elif filter['operator'] == '<=':
                queryset = queryset.filter(**{'{}__lte'.format(filter['field']): filter['value']})
            elif filter['operator'] == '>':
                queryset = queryset.filter(**{'{}__gt'.format(filter['field']): filter['value']})
            elif filter['operator'] == '>=':
                queryset = queryset.filter(**{'{}__gte'.format(filter['field']): filter['value']})
        except Exception:
            if request:
                messages.add_message(request, messages.ERROR, "Could not apply filter ({} {} {})".format(
                    filter['field'],
                    filter['operator'],
                    filter['value']
                ))
    for name, values in grouped_filter.items():
        field = field_indexed[name]
        if field['type'] == 'text':
            or_queries = [Q(**{'{}__icontains'.format(name): value}) for value in values]
            queryset = queryset.filter(reduce(operator.or_, or_queries))
        else:
            or_queries = [Q(**{name: value}) for value in values]
            queryset = queryset.filter(reduce(operator.or_, or_queries))

    return queryset
