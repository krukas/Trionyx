"""
trionyx.views
~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""

from .models import (  # noqa F401
    ListView, ListJsendView, ListExportView, ListChoicesJsendView, DetailTabView,
    DetailTabJsendView, UpdateView, CreateView, DeleteView,
)
from .dialogs import (  # noqa F401
    DialogView, UpdateDialog, CreateDialog,
)
