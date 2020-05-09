"""
trionyx.trionyx.layouts
~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from rest_framework.authtoken.models import Token
from trionyx.layout import (
    Container, Row, Column10, Column2, Column12, Column6, Component, OnclickLink,
    Panel, DescriptionList, TableDescription, Img, Table, Html, HtmlTemplate, ProgressBar
)
from trionyx.renderer import datetime_value_renderer
from trionyx.trionyx.models import AuditLogEntry, LogEntry
from trionyx.views import tabs
from .renderers import render_level


@tabs.register('trionyx.profile')
def account_overview(obj):
    """Create layout for user profile"""
    token, created = Token.objects.get_or_create(user=obj)
    return Container(
        Row(
            Column2(
                Panel(
                    _('Avatar'),
                    Img(src="{}{}".format(
                        settings.MEDIA_URL if obj.avatar else settings.STATIC_URL,
                        obj.avatar if obj.avatar else 'img/avatar.png'
                    )),
                    collapse=True,
                ),
            ),
            Column10(
                Column6(
                    Panel(
                        _('Account information'),
                        DescriptionList(
                            'email',
                            'first_name',
                            'last_name',
                        ),
                    )
                ),
                Column6(
                    Panel(
                        # TODO Add token reset button
                        _('Settings'),
                        DescriptionList(
                            {
                                'label': _('Language'),
                                'value': _(obj.get_language_display()),
                            },
                            'timezone',
                            {
                                'label': _('API Token'),
                                'value': Component(
                                    Html(token.key),
                                    OnclickLink(
                                        _('Reset'),
                                        model_url='dialog-edit-custom',
                                        model_code='reset-api-token',
                                        dialog=True,
                                        dialog_reload_layout=True,
                                    ),
                                ),
                            },
                        ),
                    )
                )
            ),
        )
    )


@tabs.register('trionyx.user')
def trionyx_user(obj):
    """Create layout for admin user"""
    from trionyx.trionyx.views import create_permission_jstree
    from django.contrib.auth.models import Permission
    permissions = []
    if obj.is_superuser:
        permissions = Permission.objects.all()
    else:
        permissions.extend(list(obj.user_permissions.all()))
        for group in obj.groups.all():
            permissions.extend(list(group.permissions.all()))

    token, created = Token.objects.get_or_create(user=obj)
    return Container(
        Row(
            Column2(
                Panel(
                    _('Avatar'),
                    Img(src="{}{}".format(
                        settings.MEDIA_URL if obj.avatar else settings.STATIC_URL,
                        obj.avatar if obj.avatar else 'img/avatar.png'
                    )),
                    collapse=True,
                ),
            ),
            Column10(
                Panel(
                    _('Account information'),
                    DescriptionList(
                        'email',
                        'first_name',
                        'last_name',
                        'created_at',
                        'last_login',
                        'last_online',
                        'is_active',
                        'is_superuser',
                        'groups',
                        {
                            'label': _('API Token'),
                            'value': Component(
                                Html(token.key),
                                OnclickLink(
                                    _('Reset'),
                                    model_url='dialog-edit-custom',
                                    model_code='reset-api-token',
                                    dialog=True,
                                    dialog_reload_layout=True,
                                ),
                            ),
                        },
                    ),
                ),
                Panel(
                    _('All active permissions'),
                    HtmlTemplate(
                        template_name='trionyx/base/permissions.html',
                        context={
                            'permission_jstree': create_permission_jstree(permissions, disabled=True),
                        },
                        css_files=['plugins/jstree/themes/default/style.css'],
                        js_files=['plugins/jstree/jstree.min.js'],
                    ),
                    id='all-active-permissions-panel',
                ),
            ),
        ),
    )


@tabs.register('auth.group')
def auth_group(obj):
    """Create layout for permission group"""
    from trionyx.trionyx.views import create_permission_jstree
    return [
        Column12(
            Panel(
                _('Info'),
                TableDescription(
                    'name'
                )
            )
        ),
        Column12(
            Panel(
                _('Permissions'),
                HtmlTemplate(
                    template_name='trionyx/base/permissions.html',
                    context={
                        'permission_jstree': create_permission_jstree(obj.permissions.all(), disabled=True),
                    },
                    css_files=['plugins/jstree/themes/default/style.css'],
                    js_files=['plugins/jstree/jstree.min.js'],
                ),
            ),
        )
    ]


@tabs.register('trionyx.log')
def trionyx_log(obj):
    """Create log layout"""
    return Container(
        Row(
            Column6(
                Panel(
                    _('Log info'),
                    TableDescription(
                        {
                            'label': _('Level'),
                            'value': render_level(obj)
                        },
                        'message',
                        {
                            'label': _('Location'),
                            'value': '{}:{}'.format(obj.file_path, obj.file_line)
                        },
                        'last_event',
                        'log_count',
                    )
                ),
                Panel(
                    _('Backtrace'),
                    Html(
                        '<pre>{}</pre>'.format(obj.traceback) if obj.traceback
                        else '<div class="alert alert-info" style="margin: 0;border-radius: 0;">No traceback</div>'
                    )
                )
            ),
            Column6(
                Panel(
                    _('Last log entries'),
                    Table(
                        obj.entries.select_related('user').order_by('-id')[:25],
                        'log_time',
                        'user',
                        'path',
                        'user_agent',
                        object=LogEntry()
                    )
                )
            )
        )
    )


@tabs.register('trionyx.task')
def task(obj):
    """Render task layout"""
    return Container(
        Row(
            Column6(
                Panel(
                    _('General'),
                    TableDescription(
                        'description',
                        'status',
                        'user',
                        'started_at',
                        {
                            'field': 'execution_time',
                            'renderer': lambda value, **options: str(timezone.timedelta(seconds=value)),
                        },
                        'result=class:pre',
                    )
                )
            ),
            Column6(
                Panel(
                    _('Process'),
                    TableDescription(
                        {
                            'field': 'progress',
                            'value': ProgressBar('progress'),
                        },
                        {
                            'field': 'progress_output',
                            'renderer': lambda value, **options: '<br/>'.join(value),
                        }
                    )
                )
            )
        )
    )


def auditlog(obj):
    """Create auditlog history layout"""
    content_type = ContentType.objects.get_for_model(obj)
    return [
        Column12(
            Panel(
                _('{action} on {date} by {user}').format(
                    action=auditlog.get_action_display(),
                    date=datetime_value_renderer(auditlog.created_at),
                    user=auditlog.user if auditlog.user else 'System'
                ),
                Table(
                    [[field, *changes] for field, changes in auditlog.changes.items()],
                    {
                        'label': _('Field'),
                        'width': '10%',
                    },
                    {
                        'label': _('Old value'),
                        'width': '45%',
                    },
                    {
                        'label': _('New value'),
                        'width': '45%',
                    },
                )
            )
        ) for auditlog in AuditLogEntry.objects.filter(content_type=content_type, object_id=obj.id).order_by('-created_at')
    ]
