"""
trionyx.core.views
~~~~~~~~~~~~~~~~~~

Core models

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
from .core import ListView, ListJsendView, DetailTabView, DetailTabJsendView, UpdateView, CreateView, DeleteView
from . import accounts

__all__ = [
    'ListView', 'ListJsendView', 'DetailTabView', 'DetailTabJsendView',
    'UpdateView', 'CreateView', 'DeleteView', 'accounts'
]
