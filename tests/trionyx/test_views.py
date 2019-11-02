from unittest.mock import patch
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from trionyx.trionyx.models import User
from trionyx.trionyx.models import Task, AuditLogEntry


class ModelsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(email='info@trionyx.com', password='top_secret')
        self.test_user = User.objects.create_user(email='test@test.com', password='top_secret')
        self.client.login(email='info@trionyx.com', password='top_secret')

    def test_profile(self):
        response = self.client.get('/account/view/')
        self.assertContains(response, 'info@trionyx.com')

    def test_edit_profile(self):
        response = self.client.get('/account/edit/')
        self.assertContains(response, 'info@trionyx.com')

    def test_post_edit_profile(self):
        response = self.client.post('/account/edit/', {
            'email': self.user.email,
            'language': 'nl',
            'timezone': 'Europe/Amsterdam',
            'first_name': 'Trionyx',
        })

        user = User.objects.get(id=self.user.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(user.first_name, 'Trionyx')

    # Global search
    def test_search(self):
        response = self.client.get('/global-search/', {
            'search': self.user.email,
        })

        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data'][0]['items'][0]['url'], self.user.get_absolute_url())

    # Filters
    def test_filters(self):
        response = self.client.get('/model-filter-fields/', {
            'id': ContentType.objects.get_for_model(User).id,
        })

        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['fields']['email']['name'], 'email')

    # Tasks
    def test_tasks(self):
        Task.objects.create(
            celery_task_id='id',
            description='Test task',
            user=self.user,
        )
        response = self.client.get('/user-tasks/')

        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data'][0]['description'], 'Test task')

    # Dashboard
    def test_dashboard(self):
        response = self.client.get('/')
        self.assertContains(response, 'tx-dashboard')

    # Mass delete
    def test_no_mass_delete(self):
        response = self.client.post('/mass/trionyx/user/delete/')
        self.assertContains(response, 'There are no items selected to be deleted, please select one or more items')

    def test_select_mass_delete(self):
        response = self.client.post('/mass/trionyx/user/delete/', {
            '__post__': 'true',
            'all': '0',
            'ids': [self.test_user.id],
            'filters': '[]',
        })

        self.assertEqual(User.objects.count(), 1)
        self.assertContains(response, 'deleted')

    def test_filter_all_mass_delete(self):
        response = self.client.post('/mass/trionyx/user/delete/', {
            '__post__': 'true',
            'all': '1',
            'ids': [],
            'filters': '[{"field": "email", "operator": "==", "value": "test@test.com"}]',
        })

        self.assertEqual(User.objects.count(), 1)
        self.assertContains(response, 'deleted')

    def test_all_mass_delete(self):
        response = self.client.post('/mass/trionyx/user/delete/', {
            '__post__': 'true',
            'all': '1',
            'ids': [],
            'filters': '[]',
        })

        # sqlite somehow doesnt remove logs when user is deleted
        AuditLogEntry.objects.get_queryset().delete()

        self.assertEqual(User.objects.count(), 0)
        self.assertContains(response, 'deleted')

    # Mass update
    def test_no_mass_update(self):
        response = self.client.get('/mass/trionyx/user/update/')
        self.assertEqual(response.status_code, 302)

    def test_select_mass_update_view(self):
        response = self.client.get('/mass/trionyx/user/update/', {
            'all': '0',
            'ids': [self.test_user.id],
            'filters': '[]',
        })

        self.assertContains(response, 'trionyxClickChange')

    def test_post_no_mass_update_view(self):
        response = self.client.post('/mass/trionyx/user/update/', {})
        self.assertEqual(response.status_code, 302)

    @patch('trionyx.trionyx.tasks.MassUpdateTask.delay')
    def test_post_not_valid_mass_update_view(self, mock_call):
        response = self.client.post('/mass/trionyx/user/update/', {
            'trionyx_all': '0',
            'trionyx_ids': [self.test_user.id],
            'trionyx_filters': '[]',

            'email': 'test',
            'change_email': '1',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(mock_call.called)

    @patch('trionyx.trionyx.tasks.MassUpdateTask.delay')
    def test_post_mass_update_view(self, mock_call):
        self.client.post('/mass/trionyx/user/update/', {
            'trionyx_all': '0',
            'trionyx_ids': [self.test_user.id],
            'trionyx_filters': '[]',

            'first_name': 'test',
            'change_first_name': '1',
        })

        self.assertTrue(mock_call.called)
