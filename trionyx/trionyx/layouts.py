"""
trionyx.trionyx.layouts
~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from trionyx.views import tabs
from trionyx.layout import (
    Container, Row, Column10, Column2, Column12, Column6, Panel, DescriptionList, TableDescription, Img, Table, Html
)

from django.conf import settings

from .renderers import render_level


@tabs.register('trionyx.profile')
def account_overview(obj):
    """Create layout for user profile"""
    return Container(
        Row(
            Column2(
                Panel(
                    'Avatar',
                    Img(src="{}{}".format(settings.MEDIA_URL, obj.avatar)),
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
                )
            ),
        )
    )


@tabs.register('trionyx.user')
def trionyx_user(obj):
    """Create layout for admin user"""
    return Container(
        Row(
            Column2(
                Panel(
                    'Avatar',
                    Img(src="{}{}".format(settings.MEDIA_URL, obj.avatar)),
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
