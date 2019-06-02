"""
trionyx.trionyx.layouts
~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from trionyx.views import tabs
from trionyx.layout import (
    Container, Row, Column10, Column2, Column12, Panel, DescriptionList, TableDescription, Img, Table
)

from django.conf import settings


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
