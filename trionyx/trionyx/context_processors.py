"""
trionyx.trionyx.context_processors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from django.conf import settings
from trionyx.menu import app_menu


def trionyx(request):
    """Add trionyx context data"""
    return {
        'TX_APP_NAME': settings.TX_APP_NAME,
        'TX_LOGO_NAME_START': settings.TX_LOGO_NAME_START,
        'TX_LOGO_NAME_END': settings.TX_LOGO_NAME_END,
        'TX_LOGO_NAME_SMALL_START': settings.TX_LOGO_NAME_SMALL_START,
        'TX_LOGO_NAME_SMALL_END': settings.TX_LOGO_NAME_SMALL_END,
        'TX_THEME_COLOR': settings.TX_THEME_COLOR,
        'tx_skin_css': 'css/skins/skin-{}.min.css'.format(settings.TX_THEME_COLOR),

        'trionyx_menu_items': app_menu.get_menu_items(request.user),
        'trionyx_menu_collapse': request.COOKIES.get('menu.state') == 'collapsed',
    }
