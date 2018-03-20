"""
trionyx.core.apps
~~~~~~~~~~~~~~~~~

Core apps package containing Appconfig

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
from django.apps import AppConfig

class BaseConfig(AppConfig):
	pass

class Config(BaseConfig):
    """Django core config app"""

    name = 'trionyx.core'
    verbose_name = 'Core'
