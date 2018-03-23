from django.apps import AppConfig

from trionyx.navigation import Menu


class BlogConfig(AppConfig):
    """Django core config app"""

    name = 'app.testblog'
    verbose_name = 'Blog'

    def ready(self):

        Menu.add_item('blog/categories', 'Categories', 'fa fa-sitemap', None, 10)
        Menu.add_item('blog/posts', 'Posts', 'fa fa-file-text', None, 20)
        Menu.add_item('blog/tags', 'Tags', 'fa fa-tag', None, 30)

        Menu.add_item('blog', 'Blog', 'fa fa-edit')

        # Test multi level tree
        Menu.add_item('multilevel/level1/categories', 'Categories', '', None, 10)
        Menu.add_item('multilevel/level1/level2/posts', 'Posts', '', None, 20)
        Menu.add_item('multilevel/level1/level2/level3/tags', 'Tags', '', None, 30)
