"""
trionyx.trionyx.forms.accounts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import password_validation
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div

from trionyx.trionyx.models import User


class UserUpdateForm(forms.ModelForm):
    """User update form"""

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
        required=False,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Init user form"""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'email',
            Div(
                Fieldset(
                    'Personal info',
                    'first_name',
                    'last_name',
                    css_class="col-md-6",
                ),
                Div(
                    'avatar',
                    css_class="col-md-6",
                ),
                css_class="row"
            ),
            Fieldset(
                'Change password',
                'new_password1',
                'new_password2',
            ),
        )

    class Meta:
        """Meta description for form"""

        model = User
        fields = ['new_password1', 'new_password2', 'email', 'first_name', 'last_name', 'avatar']

    def clean_new_password2(self):
        """Validate password when set"""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
            password_validation.validate_password(password2, self.instance)
        return password2

    def save(self, commit=True):
        """Save user"""
        user = super().save(commit=False)

        password = self.cleaned_data["new_password1"]
        if password:
            user.set_password(password)

        if commit:
            user.save()
        return user
