"""
trionyx.trionyx.management.commands.create_favicon
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import os

from PIL import Image, ImageDraw, ImageFont
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    """Command for creating favicon"""

    help = 'Create favicon'

    def handle(self, *args, **options):
        """Create new favicon"""
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        skins = {
            'blue': (0, 115, 183),
            'yellow': (243, 156, 18),
            'green': (0, 166, 90),
            'purple': (96, 92, 168),
            'red': (221, 75, 57),
            'black': (17, 17, 17),
        }
        theme = settings.TX_THEME_COLOR.replace('-light', '')
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
        img.save(os.path.join(app_dir, 'static', 'img', 'favicon.png'))
