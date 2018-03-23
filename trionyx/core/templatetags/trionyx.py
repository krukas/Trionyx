from django import template

register = template.Library()


@register.simple_tag
def active_menu_item(request, item):
    if item.is_active(request.path):
        return 'active'
    return ''