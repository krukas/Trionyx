"""
trionyx.trionyx.context_processors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from django.conf import settings
from trionyx.menu import app_menu
from trionyx import utils
from trionyx.urls import model_url
from trionyx.models import get_class


def trionyx(request):
    """Add trionyx context data"""
    return {
        'DEBUG': settings.DEBUG,
        'TX_APP_NAME': settings.TX_APP_NAME,
        'TX_LOGO_NAME_START': settings.TX_LOGO_NAME_START,
        'TX_LOGO_NAME_END': settings.TX_LOGO_NAME_END,
        'TX_LOGO_NAME_SMALL_START': settings.TX_LOGO_NAME_SMALL_START,
        'TX_LOGO_NAME_SMALL_END': settings.TX_LOGO_NAME_SMALL_END,
        'TX_THEME_COLOR': settings.TX_THEME_COLOR,
        'tx_skin_css': 'css/skins/skin-{}.min.css'.format(settings.TX_THEME_COLOR),
        'tx_tasks_url': model_url(get_class('trionyx.Task'), 'list'),

        'trionyx_menu_items': app_menu.get_menu_items(request.user),
        'trionyx_menu_collapse': request.COOKIES.get('menu.state') == 'collapsed',

        'datetime_input_format': utils.datetime_format_to_momentjs(utils.get_datetime_input_format()),
        'date_input_format': utils.datetime_format_to_momentjs(utils.get_datetime_input_format(date_only=True)),
        'current_locale': utils.get_current_locale(),
    }
