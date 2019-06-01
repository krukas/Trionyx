from trionyx.views import tabs, layouts
from trionyx.layout import Panel, Button, Column12, Table, TableDescription
from trionyx.urls import model_url

from .models import Post, Tag

@layouts.register('view')
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
                    {
                        'label': 'Update',
                        'value': Button(
                            'Delete',
                            dialog_url=model_url(obj, 'dialog-delete'),
                            dialog_options={
                                'callback': "function(){trionyx_reload_tab('general')}"
                            }
                        )
                    }
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