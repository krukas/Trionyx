from trionyx.trionyx.apps import BaseConfig


class BlogConfig(BaseConfig):
    """Django core config app"""

    name = 'app.testblog'
    verbose_name = 'Blog'

    menu_name = 'Super blog'
    menu_icon = 'fa fa-rss-square'
    menu_order = 500

    class Post:
        verbose_name = '{title}'
        search_description = '{publish_date} {title} {price}'
        list_default_fields = ['id', 'publish_date', 'title']

    class Category:
        verbose_name = '{name}'

        list_fields = [
            {
                'field': 'name',
                'renderer': lambda model, field: model.name.upper()
            }
        ]

        list_default_fields = ['id', 'created_at', 'name']

    class Tag:
        verbose_name = '{name}'
        menu_exclude = True