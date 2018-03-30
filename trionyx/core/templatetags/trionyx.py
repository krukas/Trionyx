"""
trionyx.core.templatetags.trionyx
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
from django import template

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
    return component.render(context.flatten(), context.request)
