from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag
def active_menu_item(request, item):
    if item.is_active(request.path):
        return 'active'
    return ''


@register.simple_tag(takes_context=True)
def render_component(context, component):
    return component.render(context.flatten(), context.request)
