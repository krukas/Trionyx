"""
trionyx.trionyx.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import password_validation
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from trionyx import forms
from trionyx.forms.layout import Layout, Fieldset, Div, HtmlTemplate
from trionyx.forms.helper import FormHelper
from trionyx.trionyx.models import User
from trionyx.trionyx.icons import ICON_CHOICES
from trionyx.config import models_config
from trionyx import utils


class ProfileUpdateForm(forms.ModelForm):
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

    def __init__(self, instance=None, *args, **kwargs):
        """Init user form"""
        super().__init__(*args, instance=instance, **kwargs)
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


@forms.register(default_create=True)
class UserCreateForm(forms.ModelForm):
    """User update form"""

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
        required=True,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput,
        required=True,
    )

    def __init__(self, instance=None, *args, **kwargs):
        """Init user form"""
        super().__init__(*args, instance=instance, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Fieldset(
                    'Login',
                    'email',
                    'new_password1',
                    'new_password2',
                    css_class="col-md-6",
                ),
                Fieldset(
                    'Personal info',
                    'first_name',
                    'last_name',
                    css_class="col-md-6",
                ),
                css_class="row"
            ),

        )

    class Meta:
        """Meta description for form"""

        model = User
        fields = ['new_password1', 'new_password2', 'email', 'first_name', 'last_name']

    def clean_new_password2(self):
        """Validate password when set"""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
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


@forms.register(default_edit=True)
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

    def __init__(self, instance=None, *args, **kwargs):
        """Init user form"""
        super().__init__(*args, instance=instance, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'email',
            Div(
                Fieldset(
                    'Personal info',
                    'first_name',
                    'last_name',
                    'avatar',
                    css_class="col-md-6",
                ),
                Fieldset(
                    'Permissions',
                    'is_active',
                    'is_superuser',
                    'user_permissions',
                    'groups',
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
        fields = [
            'new_password1', 'new_password2', 'email', 'first_name', 'last_name',
            'avatar', 'user_permissions', 'groups', 'is_superuser', 'is_active'
        ]

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
            self.save_m2m()
        return user


@forms.register(default_create=True, default_edit=True)
class GroupForm(forms.ModelForm):
    """Group form"""

    def __init__(self, *args, **kwargs):
        """Init GroupForm"""
        super().__init__(*args, **kwargs)  # populates the post
        self.fields['permissions'].queryset = Permission.objects.exclude(
            content_type__in=ContentType.objects.filter(
                Q(app_label__in=['contenttypes', 'sessions', 'watson'])
                | Q(app_label='auth') & Q(model='permission')  # noqa w503
                | Q(app_label='trionyx') & Q(model='auditlogentry')  # noqa w503
                | Q(app_label='trionyx') & Q(model='logentry')  # noqa w503
                | Q(app_label='trionyx') & Q(model='userattribute')  # noqa w503
            )
        )

    class Meta:
        """Meta description for form"""

        model = Group
        fields = ['name', 'permissions']


class AuditlogWidgetForm(forms.Form):
    """Auditlog widget form"""

    SHOW_CHOICES = [
        ('all', 'All'),
        ('user', 'Users only'),
        ('system', 'Systems only'),
    ]

    show = forms.ChoiceField(choices=SHOW_CHOICES)


class TotalSummaryWidgetForm(forms.Form):
    """Total summary widget form"""

    PERIOD_CHOICES = [
        ('all', 'All'),
        ('year', 'Current year'),
        ('month', 'Current month'),
        ('week', 'Current week'),
        ('day', 'Current day'),
        ('365days', 'Last 365 days'),
        ('30days', 'Last 30 days'),
        ('7days', 'Last 7 days'),
    ]

    icon = forms.ChoiceField(choices=ICON_CHOICES)

    model = forms.ChoiceField(choices=[], required=False)
    field = forms.CharField()

    period = forms.ChoiceField(choices=PERIOD_CHOICES)
    period_field = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        """Init form"""
        super().__init__(*args, **kwargs)
        content_type_map = ContentType.objects.get_for_models(*list(models_config.get_all_models(utils.get_current_request().user)))
        period_fields = {}
        summary_fields = {}

        for config in models_config.get_all_configs():
            if config.model not in content_type_map:
                continue

            summary_fields[content_type_map[config.model].id] = [
                {
                    'id': field.name,
                    'text': str(field.verbose_name)
                } for field in config.get_fields() if config.get_field_type(field) in ['int', 'float']
            ]

            period_fields[content_type_map[config.model].id] = [
                {
                    'id': field.name,
                    'text': str(field.verbose_name)
                } for field in config.get_fields(True) if config.get_field_type(field) in ['date', 'datetime']
            ]

        self.fields['model'].choices = [
            (content_type.id, model._meta.verbose_name.capitalize()) for model, content_type
            in content_type_map.items()]

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'icon',
            Div(
                Div(
                    'model',
                    css_class="col-md-6",
                ),
                Div(
                    HtmlTemplate('widgets/total_summary/form_field.html', {
                        'summary_fields': summary_fields,
                        'value': self.initial.get('field'),
                    }),
                    css_class="col-md-6",
                ),
                css_class="row"
            ),
            Div(
                Div(
                    'period',
                    css_class="col-md-6",
                ),
                Div(
                    HtmlTemplate('widgets/total_summary/period_field.html', {
                        'period_fields': period_fields,
                        'value': self.initial.get('period_field'),
                    }),
                    css_class="col-md-6",
                ),
                css_class="row"
            ),
        )
