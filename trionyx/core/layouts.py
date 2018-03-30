from trionyx.navigation import Tab
from trionyx.layout import Layout, Container, Row, Column10, Column2, Panel, DescriptionList, Img

from django.conf import settings


@Tab.register('core.profile')
def account_overview(object):
    return Layout(
        Container(
            Row(
                Column2(
                    Panel(
                        Img(src="{}{}".format(settings.MEDIA_URL, object.avatar)),
                        title='Avatar',
                        collapse=True,
                    ),
                ),
                Column10(
                    Panel(
                        DescriptionList(
                            fields=[
                                'email',
                                'first_name',
                                'last_name',
                            ]
                        ),
                        title='Account information',
                    )
                ),
            )
        )
    )
