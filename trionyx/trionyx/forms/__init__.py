"""
trionyx.core.forms
~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from django import forms
from crispy_forms.helper import FormHelper as CrispyFormHelper
from crispy_forms.layout import Layout

from trionyx import models
from trionyx.trionyx.forms import layout
from trionyx.utils import get_datetime_input_format

from .accounts import UserUpdateForm

__all__ = ['UserUpdateForm']


class FormHelper(CrispyFormHelper):
    """Form helper for Trionyx forms"""

    def build_default_layout(self, form):
        """Build default layout use custom form layouts based on field type"""
        get_model_field = form.Meta.model._meta.get_field if form.Meta.model else None

        fields = []
        for name, ffield in form.fields.items():
            field = None
            try:
                mfield = get_model_field(name)
            except Exception:
                mfield = None

            # Try get best layout based on model or form field
            if (mfield and isinstance(mfield, models.DateTimeField)) or isinstance(ffield, forms.DateTimeField):
                field = layout.DateTimePicker(name)
            elif (mfield and isinstance(mfield, models.DateField)) or isinstance(ffield, forms.DateField):
                field = layout.DateTimePicker(name, format=get_datetime_input_format(date_only=True))
            elif (mfield and isinstance(mfield, models.TimeField)) or isinstance(ffield, forms.TimeField):
                field = layout.TimePicker(field)

            fields.append(field if field else name)

        return Layout(*fields)
