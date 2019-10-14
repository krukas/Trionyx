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

        view_header_buttons = [
            {
                'label': 'Publish',  # string or function
                'url': 'trionyx:model-dialog-edit',  # string or function
                'type': 'bg-theme', # string or function
                'show': lambda obj, alias: True,  # Function that gives True or False if button must be displayed
                'modal': True,
            }
        ]

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