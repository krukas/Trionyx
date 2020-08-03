"""
trionyx.trionyx.conf
~~~~~~~~~~~~~~~~~~~~

:copyright: 2020 by Maikel Martens
:license: GPLv3
"""
from trionyx.config import AppSettings


# Defaults are set in trionyx.settings
settings = AppSettings('TX', {
    'APP_NAME': '',
    'LOGO_NAME_START': '',
    'LOGO_NAME_END': '',
    'LOGO_NAME_SMALL_START': '',
    'LOGO_NAME_SMALL_END': '',
    'THEME_COLOR': '',
    'COMPANY_NAME': '',
    'COMPANY_ADDRESS_LINES': [],
    'COMPANY_TELEPHONE': '',
    'COMPANY_WEBSITE': '',
    'COMPANY_EMAIL': '',
    'SHOW_CHANGELOG_NEW_VERSION': True,
})
