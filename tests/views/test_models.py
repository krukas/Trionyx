import io
from django.test import TestCase

from trionyx.trionyx.models import User
from trionyx.config import models_config


class ModelsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(email='info@trionyx.com', password='top_secret')
        self.test_user = User.objects.create_user(email='test@test.com', password='top_secret')
        self.client.login(email='info@trionyx.com', password='top_secret')

    def get_user_url(self, id=None, action=None):
        return '/'.join(
            filter(None, [
                '/model/trionyx/user',
                str(id) if id else False,
                action
            ])) + '/'

    # List view
    def test_listview(self):
        response = self.client.get('/model/testblog/post/')
        self.assertEqual(response.status_code, 200)

    def test_404_listview(self):
        response = self.client.get('/model/testblog/not-a-model/')
        self.assertEqual(response.status_code, 404)

    def test_403_listview(self):
        self.client.login(email='test@test.com', password='top_secret')
        response = self.client.get('/model/trionyx/user/')
        self.assertEqual(response.status_code, 403)

    def test_ajax_listview(self):
        response = self.client.get('/model/trionyx/user/ajax/')
        data = response.json()

        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['items']), 2)

    def test_ajax_listview_filters(self):
        response = self.client.post('/model/trionyx/user/ajax/', {
            'filters': '[{"field": "email", "operator": "==", "value": "info@trionyx.com"}]'
        })
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['items']), 1)

    def test_ajax_listview_invalid_json_filters(self):
        response = self.client.post('/model/trionyx/user/ajax/', {
            'filters': '{]'
        })
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['items']), 2)

    def test_ajax_listview_select_related(self):
        response = self.client.post('/model/testblog/post/ajax/', {
            'selected_fields': 'id,category,category__name'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['data']['items']), 0)

    def test_ajax_listview_search(self):
        response = self.client.post('/model/trionyx/user/ajax/', {
            'search': 'info@trionyx.com'
        })
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['items']), 1)

    def test_ajax_listview_page(self):
        response = self.client.post('/model/trionyx/user/ajax/', {
            'page_size': 1,
            'page': 2,
        })
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['items']), 1)

    def test_ajax_listview_page_to_small(self):
        response = self.client.post('/model/trionyx/user/ajax/', {
            'page': -1,
        })
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['items']), 2)

    def test_ajax_listview_page_to_big(self):
        response = self.client.post('/model/trionyx/user/ajax/', {
            'page': 9999,
        })
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['items']), 2)

    def test_ajax_listview_custom_fields(self):
        response = self.client.post('/model/trionyx/user/ajax/', {
            'selected_fields': 'id,email',
        })
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['items']), 2)
        self.assertEqual(len(data['data']['items'][0]['row_data']), 2)

    def test_ajax_listview_custom_fields_twice(self):
        self.client.post('/model/trionyx/user/ajax/', {
            'selected_fields': 'id,email',
        })
        response = self.client.post('/model/trionyx/user/ajax/', {
            'selected_fields': 'id,email',
        })
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']['items']), 2)
        self.assertEqual(len(data['data']['items'][0]['row_data']), 2)

    def test_403_ajax_listview(self):
        self.client.login(email='test@test.com', password='top_secret')
        response = self.client.get('/model/trionyx/user/ajax/')
        self.assertEqual(response.status_code, 403)

    def test_listexportview(self):
        response = self.client.post('/model/trionyx/user/download/', {
            'selected_fields': 'id,email',
        })
        content = io.StringIO((b"".join(response.streaming_content)).decode('utf-8'))
        lines = content.readlines()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(lines[0].strip(), 'id,email')
        self.assertEqual(lines[1].strip(), '{},test@test.com'.format(self.test_user.id))
        self.assertEqual(lines[2].strip(), '{},info@trionyx.com'.format(self.user.id))

    def test_listchoices(self):
        response = self.client.get('/model/trionyx/user/choices/', {
            'field': 'created_by',
        })

        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']), 2)

    def test_listchoices_nested(self):
        response = self.client.get('/model/testblog/post/choices/', {
            'field': 'category__created_by',
        })

        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']), 2)

    def test_listchoices_invalid(self):
        response = self.client.get('/model/testblog/post/choices/', {
            'field': 'category__invalid',
        })

        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(len(data['data']), 0)

    # Test detail view
    def test_detailview(self):
        response = self.client.get(self.get_user_url(self.test_user.id))
        self.assertEqual(response.status_code, 200)

    def test_404_detailview(self):
        response = self.client.get('/model/trionyx/user/9999/')
        self.assertEqual(response.status_code, 404)

    def test_tab_detailview(self):
        response = self.client.get(self.get_user_url(self.test_user.id, action='tab'), {
            'tab': 'general'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')

    def test_no_tab_detailview(self):
        response = self.client.get(self.get_user_url(self.test_user.id, action='tab'), {
            'tab': 'no-tab'
        })
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'error')

    def test_custom_header_button_detailview(self):
        config = models_config.get_config(User)
        config.header_buttons = [
            {
                'label': 'TestCustom header button',
                'url': 'trionyx:model-list',
            }
        ]

        response = self.client.get(self.get_user_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TestCustom header button')

    def test_layout_view(self):
        response = self.client.get(f'/model/trionyx/user/{self.user.id}/layout/trionyx.user-general/')
        self.assertEqual(response.status_code, 200)

    def test_layout_view_404(self):
        response = self.client.get(f'/model/trionyx/user/{self.user.id}/layout/notexists/')
        self.assertEqual(response.status_code, 404)

    def test_layout_update_complete(self):
        response = self.client.get(f'/model/trionyx/user/{self.user.id}/layout-update/trionyx.user-general/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

    def test_layout_update_selection(self):
        response = self.client.get(f'/model/trionyx/user/{self.user.id}/layout-update/trionyx.user-general/', data={
            'component': 'all-active-permissions-panel',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')

    # create/update/delete
    def test_create_view(self):
        response = self.client.get('/model/trionyx/user/create/')
        self.assertEqual(response.status_code, 200)

    def test_post_create_view(self):
        response = self.client.post('/model/trionyx/user/create/', {
            'new_password1': 'FwWBuNrZQR',
            'new_password2': 'FwWBuNrZQR',
            'email': 'new@trionyx.com',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), 3)

    def test_404_create_view(self):
        response = self.client.get('/model/trionyx/no-model/create/')
        self.assertEqual(response.status_code, 404)

    def test_update_view(self):
        response = self.client.get(self.get_user_url(self.test_user.id, action='edit'))
        self.assertEqual(response.status_code, 200)

    def test_post_update_view(self):
        response = self.client.post(self.get_user_url(self.test_user.id, action='edit'), {
            'email': self.test_user.email,
            'first_name': 'test',
            'is_active': 'True'
        })
        user = User.objects.get(id=self.test_user.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(user.first_name, 'test')

    def test_404_update_view(self):
        response = self.client.get('/model/trionyx/user/9999/edit/')
        self.assertEqual(response.status_code, 404)

    def test_delete_view(self):
        response = self.client.get(self.get_user_url(self.test_user.id, action='delete'))
        self.assertEqual(response.status_code, 200)

    def test_post_delete_view(self):
        response = self.client.post(self.get_user_url(self.test_user.id, action='delete'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), 1)

    def test_404_delete_view(self):
        response = self.client.get(self.get_user_url(9999, action='delete'))
        self.assertEqual(response.status_code, 404)
