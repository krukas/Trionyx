from django.conf import settings
from trionyx.navigation import Menu


def trionyx(request):
    return {
        'TX_APP_NAME': settings.TX_APP_NAME,
        'TX_LOGO_NAME_START': settings.TX_LOGO_NAME_START,
        'TX_LOGO_NAME_END': settings.TX_LOGO_NAME_END,
        'TX_LOGO_NAME_SMALL_START': settings.TX_LOGO_NAME_SMALL_START,
        'TX_LOGO_NAME_SMALL_END': settings.TX_LOGO_NAME_SMALL_END,

        'trionyx_menu_items': Menu.get_menu_items(),
    }
