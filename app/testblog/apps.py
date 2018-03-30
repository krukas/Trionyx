from trionyx.core.apps import BaseConfig


class BlogConfig(BaseConfig):
    """Django core config app"""

    name = 'app.testblog'
    verbose_name = 'Blog'

    menu_name = 'Super blog'
    menu_icon = 'fa fa-rss-square'
    menu_order = 500

    class Post:
        verbose_name = '{title}'
        list_default_fields = ['id', 'publish_date', 'title']
        list_search_fields = ['title', 'content']

    class Category:
        verbose_name = '{name}'

        list_fields = [
            {
                'field': 'name',
                'renderer': lambda model, field: model.name.upper()
            }
        ]

        list_default_fields = ['id', 'created_at', 'name']
        list_search_fields = ['name', 'description']

    class Tag:
        menu_exclude = True