from trionyx.navigation import tabs
from trionyx.layout import Container, Row, Column6, Panel, DescriptionList, Column12, Table, TableDescription

from .models import Post, Tag

@tabs.register(Post)
def post_overview(obj):
    return [
        Column12(
            Panel(
                "Post info",
                TableDescription(
                    'status',
                    'title',
                    'publish_date',
                    'category',
                    'tags',
                    'price',
                )
            )
        ),
        Column12(
            Panel(
                'Tags',
                Table(
                    [
                        ['list object'],
                        {
                            'name': 'dict object',
                        },
                        Tag(name='Tag object'),
                    ],
                    'name=width:120px',
                    'Value=value:fixed value',
                    {
                        'label': 'Value',
                        'value': 'fixed value',
                        'renderer': lambda value, data_object, **options: '{}'.format(data_object)
                    }
                )
            )
        )
    ]