"""
trionyx.trionyx.forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import password_validation
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType

from trionyx.models import get_class
from trionyx import forms
from trionyx.forms.layout import Layout, Fieldset, Div, HtmlTemplate, Filters, Depend, HTML  # type: ignore
from trionyx.forms.helper import FormHelper
from trionyx.trionyx.icons import ICON_CHOICES
from trionyx.config import models_config
from trionyx import utils

User = get_class('trionyx.User')


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
        self.fields['language'].choices = [(key, _(value)) for key, value in self.fields['language'].choices]
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'email',
            Div(
                Fieldset(
                    _('Personal info'),
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
            Div(
                Fieldset(
                    _('Change password'),
                    'new_password1',
                    'new_password2',
                    css_class='col-md-6'
                ),
                Fieldset(
                    _('Settings'),
                    'language',
                    'timezone',
                    css_class='col-md-6'
                ),
                css_class='row'
            ),
        )

    class Meta:
        """Meta description for form"""

        model = User
        fields = ['new_password1', 'new_password2', 'email', 'first_name', 'last_name', 'avatar', 'language', 'timezone']

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
                    _('Login'),
                    'email',
                    'new_password1',
                    'new_password2',
                    css_class="col-md-6",
                ),
                Fieldset(
                    _('Personal info'),
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

    css_files = [
        'plugins/jstree/themes/default/style.css'
    ]

    js_files = [
        'plugins/jstree/jstree.min.js'
    ]

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
        from trionyx.trionyx.views import create_permission_jstree

        selected_permissions = []
        if self.instance and self.instance.id:
            selected_permissions = self.instance.user_permissions.all()
        elif 'user_permissions' in self.initial:
            selected_permissions = self.initial['user_permissions']

        jstree = create_permission_jstree(selected_permissions)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'email',
            Div(
                Div(
                    Fieldset(
                        _('Personal info'),
                        'first_name',
                        'last_name',
                        'avatar',
                    ),
                    Fieldset(
                        _('Change password'),
                        'new_password1',
                        'new_password2',
                    ),
                    css_class="col-md-6",
                ),
                Fieldset(
                    _('Permissions'),
                    'is_active',
                    'is_superuser',
                    'groups',
                    HtmlTemplate('trionyx/forms/permissions.html', {
                        'field_name': 'user_permissions',
                        'permission_jstree': jstree,
                        'permission_ids': filter(None, [
                            item['permission_id'] for item in jstree if 'permission_id' in item]),
                    }),
                    css_class="col-md-6",
                ),
                css_class="row"
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


@forms.register(code='reset-api-token')
class UserResetApiToken(forms.ModelForm):
    """Reset API token form"""

    class Meta:
        """Meta"""

        model = User
        fields = []  # type: ignore

    def __init__(self, *args, **kwargs):
        """Init"""
        super().__init__(*args, **kwargs)
        if utils.get_current_request().user.id == self.instance.id:
            text = _('Are you sure you want to invalidate your current API key and generate a new one?')
        else:
            text = _('Are you sure you want to invalidate the API key and generate a new one for {user}?'.format(
                user=self.instance
            ))

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                HTML(text),
                css_class='alert alert-warning'
            )
        )

    def save(self, commit=True):
        """Create new token"""
        from rest_framework.authtoken.models import Token
        Token.objects.filter(user=self.instance).delete()
        Token.objects.create(user=self.instance)

    def get_title(self):
        """Form title"""
        return _('Invalidate and regenerate API token')

    def get_submit_label(self):
        """Form submit label"""
        return _('Regenerate API token')


@forms.register(default_create=True, default_edit=True)
class GroupForm(forms.ModelForm):
    """Group form"""

    css_files = [
        'plugins/jstree/themes/default/style.css'
    ]

    js_files = [
        'plugins/jstree/jstree.min.js'
    ]

    def __init__(self, *args, **kwargs):
        """Init GroupForm"""
        super().__init__(*args, **kwargs)  # populates the post
        from trionyx.trionyx.views import create_permission_jstree

        selected_permissions = []
        if self.instance:
            try:
                selected_permissions = self.instance.permissions.all()
            except ValueError:
                if 'permissions' in self.initial:
                    selected_permissions = self.initial['permissions']
        elif 'permissions' in self.initial:
            selected_permissions = self.initial['permissions']

        jstree = create_permission_jstree(selected_permissions)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            HtmlTemplate('trionyx/forms/permissions.html', {
                'field_name': 'permissions',
                'permission_jstree': jstree,
                'permission_ids': filter(None, [item['permission_id'] for item in jstree if 'permission_id' in item]),
            })
        )

    class Meta:
        """Meta description for form"""

        model = Group
        fields = ['name', 'permissions']


class AuditlogWidgetForm(forms.Form):
    """Auditlog widget form"""

    SHOW_CHOICES = [
        ('all', _('All')),
        ('user', _('Users only')),
        ('system', _('Systems only')),
    ]

    show = forms.ChoiceField(label=_('Show'), choices=SHOW_CHOICES)


class TotalSummaryWidgetForm(forms.Form):
    """Total summary widget form"""

    PERIOD_CHOICES = [
        ('all', _('All')),
        ('year', _('Current year')),
        ('month', _('Current month')),
        ('week', _('Current week')),
        ('day', _('Current day')),
        ('365days', _('Last 365 days')),
        ('30days', _('Last 30 days')),
        ('7days', _('Last 7 days')),
    ]

    icon = forms.ChoiceField(label=_('Icon'), choices=ICON_CHOICES)
    source = forms.ChoiceField(label=_('Source'), choices=[], required=True)

    model = forms.ChoiceField(label=_('Model'), choices=[], required=False)
    field = forms.CharField(label=_('Field'), required=False)

    period = forms.ChoiceField(label=_('Period'), choices=PERIOD_CHOICES)
    period_field = forms.CharField(label=_('Period field'), required=False)
    filters = forms.CharField(label=_('Filters'), required=False)

    def __init__(self, *args, **kwargs):
        """Init form"""
        super().__init__(*args, **kwargs)

        from trionyx.widgets import widget_data, TotalSummaryWidget
        self.fields['source'].choices = [
            ('', '------'),
            *[(code, data['name']) for code, data in widget_data.get_all_data(TotalSummaryWidget).items()],
            ('__custom__', _('Custom'))
        ]

        # TODO Change this to use ajax
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
            'source',
            Depend(
                [('source', r'__custom__')],
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
                Fieldset(
                    _('Filters'),
                    Filters('filters', content_type_input_id='id_model'),
                ),
                css_id='widget-custom-source'
            )
        )

    def clean(self):
        """Clean"""
        super().clean()

        if self.cleaned_data.get('source') != '__custom__':
            from trionyx.widgets import widget_data, TotalSummaryWidget
            data = widget_data.get_data(TotalSummaryWidget, self.cleaned_data.get('source'))
            if data:
                self.cleaned_data.update(data.get('options', {}))
        elif not self.cleaned_data.get('field'):
            self.add_error(None, _('Field field is required'))

        return self.cleaned_data
