"""
trionyx.trionyx
~~~~~~~~~~~~~~~

Core app for Trionyx

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import threading


LOCAL_DATA = threading.local()
"""Data storage for current request thread"""

default_app_config = 'trionyx.trionyx.apps.Config'
