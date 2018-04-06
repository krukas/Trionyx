"""
trionyx.trionyx.layouts
~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from trionyx.navigation import tabs
from trionyx.layout import Layout, Container, Row, Column10, Column2, Panel, DescriptionList, Img

from django.conf import settings


@tabs.register('trionyx.profile')
def account_overview(object):
    """Create layout for user profile"""
    return Layout(
        Container(
            Row(
                Column2(
                    Panel(
                        'Avatar',
                        Img(src="{}{}".format(settings.MEDIA_URL, object.avatar)),
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
    )
