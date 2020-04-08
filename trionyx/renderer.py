"""
trionyx.renderer
~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import os
from datetime import datetime, date
from decimal import Decimal
from functools import reduce

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.utils import formats, timezone
from babel.numbers import format_decimal, format_currency

from trionyx import utils
from trionyx import models


def date_value_renderer(value, **options):
    """Render date value with django formats, default is SHORT_DATE_FORMAT"""
    date_format = options.get('date_format', 'SHORT_DATE_FORMAT')
    return formats.date_format(value, date_format)


def datetime_value_renderer(value, **options):
    """Render datetime value with django formats, default is SHORT_DATETIME_FORMAT"""
    datetime_format = options.get('datetime_format', 'SHORT_DATETIME_FORMAT')
    if timezone.is_naive(value):
        value = timezone.make_aware(value)
    return formats.date_format(timezone.localtime(value), datetime_format)


def number_value_renderer(value, **options):
    """Format decimal value, with current locale"""
    return format_decimal(value if value else 0.0, locale=utils.get_current_locale())


def price_value_renderer(value, currency=None, **options):
    """Format price value, with current locale and CURRENCY in settings"""
    if not currency:
        currency = getattr(settings, 'CURRENCY', 'USD')
    return format_currency(value if value else 0.0, currency, locale=utils.get_current_locale())


def bool_value_renderer(value, **options):
    """Render boolean value"""
    if options.get('no_html', False):
        return value

    return '<i class="fa {} {}"></i>'.format(
        'fa-check-square-o' if value else 'fa-square-o',
        'text-success' if value else 'text-danger'
    )


def list_value_renderer(value, **options):
    """Render list value"""
    return ', '.join(map(str, value))


def related_field_renderer(value, **options):
    """Render list of related items"""
    return ', '.join(str(obj) for obj in value.all())


def file_field_renderer(file, **options):
    """Render file field as link"""
    if not file:
        return ''

    if options.get('no_html', False):
        return file.url

    return '<a href="{file.url}" target="_blank">{name}</a>'.format(file=file, name=os.path.basename(file.path))


def url_field_renderer(value, **options):
    """Render url field"""
    if options.get('no_html', False):
        return value
    return '<a href="{url}" target="_blank">{url}</a>'.format(url=value) if value else ''


def email_field_renderer(value, **options):
    """Render email field"""
    if options.get('no_html', False):
        return value
    return '<a href="mailto:{email}" target="_blank">{email}</a>'.format(email=value) if value else ''


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

    def __format__(self, format_spec):
        """Format field"""
        return getattr(self.obj, self.field_name).__format__(format_spec) if format_spec else self.__str__()


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
        renderer = self.renderers.get(type(value), lambda value, **options: str(value) if value else '')
        return renderer(value, **options)

    def render_field(self, obj, field_name, **options):
        """Render field"""
        field_parts = field_name.split('__')
        if len(field_parts) > 1:
            field_name = field_parts[-1]
            obj = reduce(lambda obj, name: getattr(obj, name), field_parts[:-1], obj)

        try:
            field = obj._meta.get_field(field_name)
        except (FieldDoesNotExist, AttributeError):
            return getattr(obj, field_name, '')

        if hasattr(field, 'choices') and getattr(field, 'choices'):
            return getattr(obj, 'get_{}_display'.format(field_name))()

        value = getattr(obj, field_name, '')
        renderer = self.renderers.get(type(field))

        if renderer:
            return renderer(value, **options)

        return self.render_value(value, **options)


renderer = Renderer({
    date: date_value_renderer,
    datetime: datetime_value_renderer,
    Decimal: number_value_renderer,
    float: number_value_renderer,
    int: number_value_renderer,
    bool: bool_value_renderer,
    list: list_value_renderer,
    models.PriceField: price_value_renderer,
    models.ManyToManyField: related_field_renderer,
    models.FileField: file_field_renderer,
    models.URLField: url_field_renderer,
    models.EmailField: email_field_renderer,
})
