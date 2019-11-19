"""
trionyx.signals
~~~~~~~~~~~~~~~

:copyright: 2019 by Maikel Martens
:license: GPLv3
"""
from django.dispatch import Signal

# NOTE: can_view signal wont work for list view or queryset
# NOTE: can_add, can_change, can_delete only works for the interface
# NOTE: can_change, can_delete wont work for mass update/delete
can_view = Signal(providing_args=["instance"])
can_add = Signal(providing_args=["instance"])
can_change = Signal(providing_args=["instance"])
can_delete = Signal(providing_args=["instance"])
