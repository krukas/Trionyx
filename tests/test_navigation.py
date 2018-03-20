from django.test import TestCase

from trionyx.navigation import Menu, MenuItem


class UtilsTestCase(TestCase):
    def setUp(self):
        Menu._root_item = None

    def test_merge_menu_item(self):
        item1 = MenuItem(
            path='item1',
            name='item1',
            icon='item1',
            url='item1',
            order=10,
            permission='item1'
        )
        item2 = MenuItem(
            path='item1',
            name='item2',
            icon='item2',
            order=20,
        )

        item1.merge(item2)
        self.assertEquals(item1.path, 'item1')
        self.assertEquals(item1.name, 'item2')
        self.assertEquals(item1.icon, 'item2')
        self.assertEquals(item1.order, 20)

    def test_complete_merge_menu_item(self):
        item1 = MenuItem(
            path='item1',
            name='item1',
            icon='item1',
            url='item1',
            order=10,
            permission='item1'
        )
        item2 = MenuItem(
            path='item1',
            name='item2',
            icon='item2',
            url='item2',
            order=20,
            permission='item2'
        )

        item1.merge(item2)
        self.assertEquals(item1.path, 'item1')
        self.assertEquals(item1.name, 'item2')
        self.assertEquals(item1.icon, 'item2')
        self.assertEquals(item1.url, 'item2')
        self.assertEquals(item1.order, 20)
        self.assertEquals(item1.permission, 'item2')

    def test_add_menu_item(self):
        Menu.add_item('/test', 'test')
        items = Menu.get_menu_items()

        self.assertEquals(len(items), 1)
        self.assertEquals(items[0].name, 'test')

    def test_add_sub_menu_path(self):
        Menu.add_item('/test/sub', 'sub')
        items = Menu.get_menu_items()

        # Test first item
        self.assertEquals(len(items), 1)
        self.assertEquals(items[0].name, 'Test')
        self.assertEquals(items[0].path, '/test')
        self.assertEquals(len(items[0].childs), 1)

        # Test sub item
        self.assertEquals(items[0].childs[0].name, 'sub')
        self.assertEquals(items[0].childs[0].path, '/test/sub')

    def test_add_same_menu_sub_path(self):
        Menu.add_item('/test/sub', 'sub')
        Menu.add_item('/test/sub2', 'sub2')
        items = Menu.get_menu_items()

        self.assertEquals(len(items), 1)
        
        # Test first item
        self.assertEquals(items[0].name, 'Test')
        self.assertEquals(items[0].path, '/test')
        self.assertEquals(len(items[0].childs), 2)

        # Test first sub item
        self.assertEquals(items[0].childs[0].name, 'sub')
        self.assertEquals(items[0].childs[0].path, '/test/sub')

        # Test first sub item
        self.assertEquals(items[0].childs[1].name, 'sub2')
        self.assertEquals(items[0].childs[1].path, '/test/sub2')

    def test_add_menu_merge(self):
        Menu.add_item('/test', 'test')
        Menu.add_item('/test', 'New name', order=10)
        items = Menu.get_menu_items()

        self.assertEquals(len(items), 1)
        self.assertEquals(items[0].name, 'New name')
        self.assertEquals(items[0].path, '/test')
        self.assertEquals(items[0].order, 10)

    def test_add_menu_item_order(self):
        Menu.add_item('/first', 'first', order=10)
        Menu.add_item('/third', 'third')
        Menu.add_item('/second', 'second', order=20)
        items = Menu.get_menu_items()

        self.assertEquals(len(items), 3)
        self.assertEquals(items[0].name, 'first')
        self.assertEquals(items[1].name, 'second')
        self.assertEquals(items[2].name, 'third')
