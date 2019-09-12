"""
trionyx.trionyx.layouts
~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from rest_framework.authtoken.models import Token
from trionyx.layout import (
    Container, Row, Column10, Column2, Column12, Column6, Panel, DescriptionList, TableDescription, Img, Table, Html
)
from trionyx.renderer import datetime_value_renderer
from trionyx.trionyx.models import AuditLogEntry
from trionyx.views import tabs
from .renderers import render_level


@tabs.register('trionyx.profile')
def account_overview(obj):
    """Create layout for user profile"""
    token, _ = Token.objects.get_or_create(user=obj)
    return Container(
        Row(
            Column2(
                Panel(
                    'Avatar',
                    Img(src="{}{}".format(
                        settings.MEDIA_URL if obj.avatar else settings.STATIC_URL,
                        obj.avatar if obj.avatar else 'img/avatar.png'
                    )),
                    collapse=True,
                ),
            ),
            Column10(
                Panel(
                    'Account information',
                    DescriptionList(
                        'email',
                        'first_name',
                        'last_name',
                    ),
                ),
                Panel(
                    # TODO Add token reset button
                    'API',
                    DescriptionList(
                        {
                            'label': 'Token',
                            'value': token.key,
                        }
                    ),
                )
            ),
        )
    )


@tabs.register('trionyx.user')
def trionyx_user(obj):
    """Create layout for admin user"""
    token, _ = Token.objects.get_or_create(user=obj)
    return Container(
        Row(
            Column2(
                Panel(
                    'Avatar',
                    Img(src="{}{}".format(
                        settings.MEDIA_URL if obj.avatar else settings.STATIC_URL,
                        obj.avatar if obj.avatar else 'img/avatar.png'
                    )),
                    collapse=True,
                ),
            ),
            Column10(
                Panel(
                    'Account information',
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
                    'permissions',
                    Table(
                        obj.user_permissions.select_related('content_type'),
                        {
                            'field': 'name',
                            'label': 'Permission',
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
                'info',
                TableDescription(
                    'name'
                )
            )
        ),
        Column12(
            Panel(
                'permissions',
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
                    'Log info',
                    TableDescription(
                        {
                            'label': 'Level',
                            'value': render_level(obj)
                        },
                        'message',
                        {
                            'label': 'Location',
                            'value': '{}:{}'.format(obj.file_path, obj.file_line)
                        },
                        'last_event',
                        'log_count',
                    )
                ),
                Panel(
                    'Backtrace',
                    Html(
                        '<pre>{}</pre>'.format(obj.traceback) if obj.traceback
                        else '<div class="alert alert-info" style="margin: 0;border-radius: 0;">No traceback</div>'
                    )
                )
            ),
            Column6(
                Panel(
                    'Last log entries',
                    Table(
                        obj.entries.select_related('user').order_by('-id')[:25],
                        'log_time',
                        'user',
                        'user_agent',
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
                '{action} on {date} by {user}'.format(
                    action=auditlog.get_action_display(),
                    date=datetime_value_renderer(auditlog.created_at),
                    user=auditlog.user if auditlog.user else 'System'
                ),
                Table(
                    [[field, *changes] for field, changes in auditlog.changes.items()],
                    {
                        'label': 'Field',
                        'width': '10%',
                    },
                    {
                        'label': 'Old value',
                        'width': '45%',
                    },
                    {
                        'label': 'New value',
                        'width': '45%',
                    },
                )
            )
        ) for auditlog in AuditLogEntry.objects.filter(content_type=content_type, object_id=obj.id).order_by('-created_at')
    ]
