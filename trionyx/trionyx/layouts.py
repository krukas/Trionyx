"""
trionyx.trionyx.layouts
~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from rest_framework.authtoken.models import Token
from trionyx.layout import (
    Container, Row, Column10, Column2, Column12, Column6, Panel, DescriptionList, TableDescription, Img, Table, Html
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
                                'value': token.key,
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
                    ),
                ),
                Panel(
                    _('Permissions'),
                    Table(
                        obj.user_permissions.select_related('content_type'),
                        {
                            'field': 'name',
                            'label': _('Permission'),
                            'renderer': lambda value, data_object, *args, **kwargs: str(data_object)
                        }
                    ),
                ),
            ),
        ),
    )


@tabs.register('auth.group')
def auth_group(obj):
    """Create layout for permission group"""
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
                Table(
                    obj.permissions.select_related('content_type'),
                    {
                        'field': 'name',
                        'label': 'Permission',
                        'renderer': lambda value, data_object, *args, **kwargs: str(data_object)
                    }
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
                        'user_agent',
                        object=LogEntry()
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
