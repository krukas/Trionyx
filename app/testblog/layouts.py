from trionyx.views import tabs, layouts
from trionyx.layout import *
from trionyx.urls import model_url

from .models import Post, Tag

@layouts.register('view')
@tabs.register(Post)
def post_overview(obj):
    return [
        Column6(
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
                            'Update',
                            url=model_url(obj, 'dialog-edit'),
                            dialog=True,
                            dialog_options={
                                'callback': "function(){trionyx_reload_tab('general')}"
                            },
                            color=Colors.TEAL,
                        )
                    },
                )
            )
        ),
        Column6(
            Panel(
                'Components',
                TableDescription(
                    {
                        'label': 'img',
                        'value': Img(
                            src='https://www.python.org/static/img/python-logo.png',
                            width='200px',
                        ),
                    },
                    {
                        'label': 'Input',
                        'value': Input(name='test')
                    },
                    {
                        'label': 'Badges',
                        'value': Component(
                            Badge('status', color=Colors.THEME),
                            Badge('status', color=Colors.LIGHT_BLUE),
                            Badge('status', color=Colors.AQUA),
                            Badge('status', color=Colors.GREEN),
                            Badge('status', color=Colors.YELLOW),
                            Badge('status', color=Colors.RED),
                            Badge('status', color=Colors.GRAY),
                            Badge('status', color=Colors.NAVY),
                            Badge('status', color=Colors.TEAL),
                            Badge('status', color=Colors.PURPLE),
                            Badge('status', color=Colors.ORANGE),
                            Badge('status', color=Colors.MAROON),
                            Badge('status', color=Colors.BLACK),
                        )
                    },
                    {
                        'label': 'Alerts',
                        'value': Component(
                            Alert('Warning with no_margin', alert=Alert.INFO,no_margin=True),
                            Alert('success', alert=Alert.SUCCESS),
                            Alert('warning', alert=Alert.WARNING),
                            Alert('danger', alert=Alert.DANGER),
                        )
                    },
                    {
                        'label': 'Thumbnail',
                        'value': Thumbnail(
                            'https://www.python.org/static/img/python-logo.png',
                            url=model_url(obj, 'dialog-edit'),
                            dialog=True,
                            dialog_options={
                                'callback': "function(){trionyx_reload_tab('general')}"
                            },
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
                    },
                    footer=[
                        [
                            ['Subtotaal', '12,50'],
                            ['Totaal', '12,50'],
                        ],
                        {
                            'colspan': 2,
                            'class': 'text-right'
                        },
                        'Price'
                    ]
                )
            )
        )
    ]

@tabs.register_update('trionyx.user', 'general')
def tasks_update(layout, obj):
    layout.add_component(Panel('Inserted'), path='container.row.column10[1].panel')
