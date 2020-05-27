from django.test import TestCase
from rest_framework.test import APIClient

from trionyx.trionyx.models import User


class ApiTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(email='info@trionyx.com', password='top_secret')
        self.client.login(email='info@trionyx.com', password='top_secret')
        self.api = APIClient()
        self.api.login(email='info@trionyx.com', password='top_secret')

    def test_api_browser(self):
        response = self.client.get('/api/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'redoc')

    def test_api_create(self):
        response = self.api.post('/api/trionyx/user/', {
            'email': 'new@trionyx.com'
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.filter(email='new@trionyx.com').count(), 1)

    def test_api_list(self):
        response = self.client.get('/api/trionyx/user/')
        self.assertEqual(response.json()['count'], 1)

    def test_api_list_search(self):
        response = self.client.get('/api/trionyx/user/', {
            '_search': 'info'
        })
        self.assertEqual(response.json()['count'], 1)

    def test_api_list_search_empty(self):
        response = self.client.get('/api/trionyx/user/', {
            '_search': 'nothing'
        })
        self.assertEqual(response.json()['count'], 0)

    def test_api_get(self):
        response = self.client.get(f'/api/trionyx/user/{self.user.id}/')
        self.assertEqual(response.json()['email'], self.user.email)
