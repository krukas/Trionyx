"""
trionyx.trionyx.templatetags.trionyx
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import json
from datetime import date

from django import template
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe

from trionyx.renderer import price_value_renderer

register = template.Library()


@register.simple_tag
def active_menu_item(request, item):
    """Check if given menu item is active"""
    if item.is_active(request.path):
        return 'active'
    return ''


@register.simple_tag(takes_context=True)
def render_component(context, component):
    """Render given component"""
    return component.render(context.flatten(), context.get('request'))


@register.filter
def jsonify(obj):
    """Jsonify given input"""
    if isinstance(obj, QuerySet):
        return mark_safe(serialize('json', obj))
    return mark_safe(json.dumps(obj))


@register.simple_tag
def model_url(model, view_name, code=None):
    """Short cut for generating model urls"""
    from trionyx.urls import model_url
    return model_url(model, view_name, code)


@register.filter
def is_date(value):
    """Check if value is date object"""
    return isinstance(value, date)


@register.filter
def price(value):
    """Render value in current locale with configured currency"""
    return mark_safe(price_value_renderer(value))
