"""
trionyx.trionyx.templatetags.trionyx
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import json
from django import template
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe

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
    if isinstance(obj, QuerySet):
        return mark_safe(serialize(obj))
    return mark_safe(json.dumps(obj))