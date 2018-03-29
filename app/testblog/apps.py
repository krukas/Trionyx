from trionyx.core.apps import BaseConfig

from trionyx.navigation import Menu


class BlogConfig(BaseConfig):
    """Django core config app"""

    name = 'app.testblog'
    verbose_name = 'Blog'

    menu_icon = 'fa-rss-square'

    def ready(self):

        Menu.add_item('blog/categories', 'Categories', 'fa fa-sitemap', None, 10)
        Menu.add_item('blog/posts', 'Posts', 'fa fa-file-text', None, 20)
        Menu.add_item('blog/tags', 'Tags', 'fa fa-tag', None, 30)

        Menu.add_item('blog', 'Blog', 'fa fa-edit')

        # Test multi level tree
        Menu.add_item('multilevel/level1/categories', 'Categories', '', None, 10)
        Menu.add_item('multilevel/level1/level2/posts', 'Posts', '', None, 20)
        Menu.add_item('multilevel/level1/level2/level3/tags', 'Tags', '', None, 30)


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