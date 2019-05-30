"""
trionyx.renderer
~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import os
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.utils import formats, timezone
from babel.numbers import format_decimal, format_currency

from trionyx import utils
from trionyx import models


def datetime_value_renderer(value, **options):
    """Render datetime value with django formats, default is SHORT_DATETIME_FORMAT"""
    datetime_format = options.get('datetime_format', 'SHORT_DATETIME_FORMAT')
    return formats.date_format(timezone.localtime(value), datetime_format)


def number_value_renderer(value, **options):
    """Format decimal value, with current locale"""
    return format_decimal(value if value else 0.0, locale=utils.get_current_locale())


def price_value_renderer(value, currency=None, **options):
    """Format price value, with current locale and CURRENCY in settings"""
    if not currency:
        currency = getattr(settings, 'CURRENCY', 'USD')
    return format_currency(value if value else 0.0, currency, locale=utils.get_current_locale())


def related_field_renderer(value, **options):
    """Render list of related items"""
    return ', '.join(str(obj) for obj in value.all())


def file_field_renderer(file, **options):
    """Render file field as link"""
    if not file:
        return ''

    return '<a href="{file.url}" target="_blank">{name}</a>'.format(file=file, name=os.path.basename(file.path))


class LazyFieldRenderer:
    """Performs render action when __str__ is called"""

    def __init__(self, obj, field_name, **options):
        """Init"""
        self.obj = obj
        self.field_name = field_name
        self.options = options

    def __str__(self):
        """Render field"""
        result = renderer.render_field(self.obj, self.field_name, **self.options)
        return str(result) if result is not None else ''


class Renderer:
    """Registry to hold all renderer's"""

    def __init__(self, renderers=None):
        """Init Renderer"""
        self.renderers = renderers if renderers else {}

    def register(self, type, renderer):
        """Register render function for value or field type"""
        self.renderers[type] = renderer

    def render_value(self, value, **options):
        """Render value"""
        renderer = self.renderers.get(type(value), lambda value, **options: value)
        return renderer(value, **options)

    def render_field(self, obj, field_name, **options):
        """Render field"""
        try:
            field = obj._meta.get_field(field_name)
        except FieldDoesNotExist:
            return getattr(obj, field_name, '')

        if hasattr(field, 'choices') and getattr(field, 'choices'):
            return getattr(obj, 'get_{}_display'.format(field_name))()

        value = getattr(obj, field_name, '')
        renderer = self.renderers.get(type(field))

        if renderer:
            return renderer(value, **options)

        if isinstance(value, models.BaseModel):
            value = str(value)

        return self.render_value(value, **options)


renderer = Renderer({
    datetime: datetime_value_renderer,
    Decimal: number_value_renderer,
    float: number_value_renderer,
    int: number_value_renderer,
    models.PriceField: price_value_renderer,
    models.ManyToManyField: related_field_renderer,
    models.FileField: file_field_renderer,
})
