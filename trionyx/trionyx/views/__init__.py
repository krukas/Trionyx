"""
trionyx.trionyx.views
~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from .core import (
    ListView, ListJsendView, DetailTabView, DetailTabJsendView, UpdateView, CreateView, DeleteView,
    DialogView, CreateDialog, UpdateDialog
)
from . import accounts

__all__ = [
    'ListView', 'ListJsendView', 'DetailTabView', 'DetailTabJsendView', 'UpdateView',
    'CreateView', 'DeleteView', 'accounts', 'DialogView', 'CreateDialog', 'UpdateDialog',
]
