"""
trionyx.trionyx.context_processors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import os
import base64

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.conf import settings
from django.apps import apps
from trionyx.menu import app_menu
from trionyx import utils
from trionyx.urls import model_url
from trionyx.models import get_class
from trionyx import __version__

from trionyx.trionyx.conf import settings as tx_settings


def offline_context():
    """Offline context used by compress"""
    locale, *_ = utils.get_current_locale().split('_')
    context = {
        'STATIC_URL': settings.STATIC_URL,
        'tx_offline_skin_css': 'css/skins/skin-{}.min.css'.format(settings.TX_THEME_COLOR),
        'apps_css_files': [],
        'apps_js_files': [],
        'offline_summernote_language_js': 'plugins/summernote/lang/summernote-{}-{}.min.js'.format(
            locale, locale.upper()
        ) if locale != 'en' else '',
    }
    for app in apps.get_app_configs():
        context['apps_css_files'].extend(getattr(app, 'css_files', []))
        context['apps_js_files'].extend(getattr(app, 'js_files', []))

    return [context]


def generate_base64_favicon():
    """Generate base64 favicon"""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    skins = {
        'blue': (0, 115, 183),
        'yellow': (243, 156, 18),
        'green': (0, 166, 90),
        'purple': (96, 92, 168),
        'red': (221, 75, 57),
        'black': (17, 17, 17),
    }
    theme = tx_settings.THEME_COLOR.replace('-light', '')
    color = skins.get(theme, (17, 17, 17))

    text = '{}{}'.format(
        settings.TX_LOGO_NAME_SMALL_START.upper(),
        settings.TX_LOGO_NAME_SMALL_END.lower()
    )

    img = Image.new('RGB', (32, 32), color=color)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(os.path.join(app_dir, 'static', 'fonts', 'pt-mono.bold.ttf'), 24)

    text_width, text_height = draw.textsize(text, font)
    position = ((32 - text_width) / 2, (32 - 5 - text_height) / 2)
    draw.text(position, text, (255, 255, 255), font=font)

    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()


tx_base64_icon = generate_base64_favicon()


def trionyx(request):
    """Add trionyx context data"""
    locale, *_ = utils.get_current_locale().split('_')
    return {
        'DEBUG': settings.DEBUG,
        'TX_APP_NAME': tx_settings.APP_NAME,
        'TX_LOGO_NAME_START': tx_settings.LOGO_NAME_START,
        'TX_LOGO_NAME_END': tx_settings.LOGO_NAME_END,
        'TX_LOGO_NAME_SMALL_START': tx_settings.LOGO_NAME_SMALL_START,
        'TX_LOGO_NAME_SMALL_END': tx_settings.LOGO_NAME_SMALL_END,
        'TX_THEME_COLOR': tx_settings.THEME_COLOR,
        'tx_base64_icon': tx_base64_icon,
        'tx_tasks_url': model_url(get_class('trionyx.Task'), 'list'),
        'tx_version': __version__,
        'tx_show_changelog': (
            tx_settings.SHOW_CHANGELOG_NEW_VERSION
            and request.user.is_authenticated
            and request.user.get_attribute('trionyx_last_shown_version') != utils.get_app_version()),

        'trionyx_menu_items': app_menu.get_menu_items(request.user),
        'trionyx_menu_collapse': request.COOKIES.get('menu.state') == 'collapsed',
        'tx_custom_skin_css': 'css/skins/skin-{}.min.css'.format(
            tx_settings.THEME_COLOR
        ) if settings.TX_THEME_COLOR != tx_settings.THEME_COLOR else '',

        'app_version': utils.get_app_version(),

        'datetime_input_format': utils.datetime_format_to_momentjs(utils.get_datetime_input_format()),
        'date_input_format': utils.datetime_format_to_momentjs(utils.get_datetime_input_format(date_only=True)),
        'current_locale': utils.get_current_locale(),
        'summernote_language': '{}-{}'.format(locale, locale.upper()),
        'summernote_language_js': 'plugins/summernote/lang/summernote-{}-{}.min.js'.format(
            locale, locale.upper()
        ) if locale != 'en' and utils.get_current_language() != settings.LANGUAGE_CODE else '',

        **offline_context()[0]
    }
