from trionyx.views import tabs, layouts, sidebars
from trionyx.layout import *
from trionyx.urls import model_url
from trionyx import models
from django.db.models.functions import TruncDay
from trionyx.renderer import price_value_renderer

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
                            # dialog_options={
                            #     'callback': "function(){trionyx_reload_tab('general')}"
                            # },
                            dialog_reload_layout='table-description',
                            color=Colors.TEAL,
                        )
                    },
                    {
                        'label': 'Sidebar',
                        'value': Button(
                            'Sidebar',
                            model_url='sidebar',
                            model_code='item',
                            sidebar=True,
                        )
                    },
                )
            ),
            Panel(
                'Charts',
                LineChart(
                    Post.objects.order_by('-sale_date'),
                    'sale_date',
                    'price',
                ),
                LineChart(
                    Post.objects.annotate(day=TruncDay('publish_date')).values(
                        'day').annotate(sum_price=models.Sum('price')).values('day', 'sum_price').order_by('-day'),
                    'day',
                    {
                        'label': 'Total price per day',
                        'field': 'sum_price',
                        'renderer': price_value_renderer,
                    },
                    time_unit='day',
                ),
                LineChart(
                    'tags',
                    'name',
                    'id',
                ),
                BarChart(
                    Post.objects.annotate(day=TruncDay('publish_date')).values('day'
                    ).annotate(
                        sum_price=models.Sum('price'),
                        sum_id=models.Sum('id')).values('day', 'sum_price', 'sum_id').order_by('-day'),
                    'day',
                    {
                        'label': 'Total price per day',
                        'field': 'sum_price',
                        'renderer': price_value_renderer,
                    },
                    'sum_id',
                    time_unit='day',
                ),
                DoughnutChart(
                    [['Python3', 60], ['Javascript', 30], ['Sql', 10]],
                    'name',
                    'value',
                ),
                PieChart(
                    [['Python3', 60], ['Javascript', 30], ['Sql', 10]],
                    'name',
                    'value',
                ),
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
                    },
                    {
                        'label': 'ProgressBar',
                        'value': Component(
                            ProgressBar(value=543, max_value=2400),
                            ProgressBar(value=20, size='xs'),
                            ProgressBar(value=78, active=True, color=Colors.GREEN),
                        ),
                    },
                    {
                        'label': 'Lists',
                        'value': UnorderedList(
                            'title',
                            'content',
                            {
                                'value': 'Fixed value'
                            },
                            {
                                'label': 'Unordered sublist',
                                'value': UnorderedList(
                                    'status',
                                    {
                                        'label': 'Another unordered sublist',
                                        'value': UnorderedList(
                                            'price'
                                        ),
                                    }
                                )
                            },
                            {
                                'label': 'Ordered sublist',
                                'value': OrderedList(
                                    'status',
                                    {
                                        'label': 'Another ordered sublist',
                                        'value': OrderedList(
                                            'price'
                                        ),
                                    }
                                )
                            },
                            {
                                'label': 'tags',
                                'value': UnorderedList(
                                    'name',
                                    objects='tags'
                                ),
                            }
                        )
                    },
                    id="table-description"
                ),
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
                        'renderer': lambda value, data_object, **options: '{}'.format(data_object),
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
                    ],
                    hover=True,
                ),
                collapse=True,
            )
        )
    ]

@tabs.register_update('trionyx.user', 'general')
def tasks_update(layout, obj):
    layout.add_component(Panel('Inserted'), path='container.row.column10[1].panel')


@sidebars.register(Post, 'item')
def item_sidebar(request, obj):
    layout = post_overview(obj)


    return {
        'title': str(obj),
        'fixed_content': 'Some fixed content 2',
        'content': 'Real content <br>' * 100,
        'theme': 'light',
        'hover': False,
        'actions': [
            {
                'label': 'Save',
                'class': 'text-success text-bold',
                'url': model_url(obj, 'dialog-edit'),
                'dialog': True,
                'dialog_options': {},
                'reload': True,
            },
            {
                'label': 'Warning',
                'class': 'text-warning',
                'url': model_url(obj, 'dialog-edit'),
                'dialog': True,
                'dialog_options': {},
                'reload': True,
            },
            {
                'label': 'Info',
                'class': 'text-info',
                'url': model_url(obj, 'dialog-edit'),
                'dialog': True,
                'dialog_options': {},
                'reload': True,
            },
            {
                'label': 'Delete',
                'class': 'text-danger',
                'url': model_url(obj, 'dialog-edit'),
                'dialog': True,
                'dialog_options': {},
                'reload': True,
                'divider': True,
            }
        ]
    }