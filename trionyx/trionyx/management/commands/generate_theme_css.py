"""
trionyx.trionyx.management.commands.create_app
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Command for creating base Trionyx app"""

    help = 'Generate theme color fixes'

    def handle(self, *args, **options):
        """Create CSS"""
        skins = {
            'blue': '#0073b7',
            'yellow': '#f39c12',
            'green': '#00a65a',
            'purple': '#605ca8',
            'red': '#dd4b39',
            'black': '#111111',
        }

        css_color_selectors = {
            'background': {
                'css': [
                    'background-color: {color} !important;',
                    'color: #ffffff !important;'
                ],
                'selectors': [
                    '.bg-theme',
                    '.nav-pills > li.active > a',
                    '.pagination > li.active > a',
                    '.select2-container--default .select2-results__option--highlighted[aria-selected]',
                    '.select2-container--default .select2-selection--multiple .select2-selection__choice',
                    '.bootstrap-datetimepicker-widget table td.active',
                    '.box.box-solid.box-theme > .box-header',
                    '.progress-bar-theme',
                ]
            },
            'border': {
                'css': [
                    'border-color: {color} !important;'
                ],
                'selectors': [
                    '.select2-container--default.select2-container--focus .select2-selection--multiple',
                    '.select2-container--default .select2-search--dropdown .select2-search__field',
                    '.select2-container--default .select2-selection--multiple .select2-selection__choice',
                    '.nav-pills > li.active > a',
                    '.pagination > li.active > a',
                    '.box-theme',
                    '.form-control:focus',
                ]
            },
            'text': {
                'css': [
                    'color: {color} !important;',
                ],
                'selectors': [
                    '.text-theme',
                    '.bootstrap-datetimepicker-widget a',
                ],
            }
        }

        for skin, color in skins.items():
            for _, config in css_color_selectors.items():
                self.stdout.write(',\n'.join([
                    *['.skin-{} {}'.format(skin, s) for s in config['selectors']],
                    *['.skin-{}-light {}'.format(skin, s) for s in config['selectors']],
                ]))
                self.stdout.write('{')
                for css in config['css']:
                    self.stdout.write('    ' + css.format(color=color))
                self.stdout.write('}\n\n')
