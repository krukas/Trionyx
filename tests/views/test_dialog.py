from django.test import TestCase

from trionyx.trionyx.models import User


class ModelsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(email='info@trionyx.com', password='top_secret')
        self.test_user = User.objects.create_user(email='test@test.com', password='top_secret')
        self.client.login(email='info@trionyx.com', password='top_secret')

    def get_user_url(self, id, action=None):
        return '/'.join(
            filter(None, [
                '/dialog/model/trionyx/user',
                str(id),
                action
            ])) + '/'

    # Update Dialog
    def test_update_dialog(self):
        response = self.client.get(self.get_user_url(self.test_user.id, action='edit'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_user.email)

    def test_post_update_dialog(self):
        response = self.client.post(self.get_user_url(self.test_user.id, action='edit'), {
            'email': self.test_user.email,
            'first_name': 'test',
            'is_active': 'True'
        })
        user = User.objects.get(id=self.test_user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(user.first_name, 'test')
        self.assertContains(response, 'alert-success')

    def test_404_update_dialog(self):
        response = self.client.get('/dialog/model/trionyx/user/9999/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Could not load')

    # Create dialog
    def test_create_dialog(self):
        response = self.client.get('/dialog/model/trionyx/user/create/')
        self.assertEqual(response.status_code, 200)

    def test_post_create_dialog(self):
        response = self.client.post('/dialog/model/trionyx/user/create/', {
            'new_password1': 'FwWBuNrZQR',
            'new_password2': 'FwWBuNrZQR',
            'email': 'new@trionyx.com',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'alert-success')
        self.assertEqual(User.objects.count(), 3)

    def test_404_create_dialog(self):
        response = self.client.get('/dialog/model/trionyx/no-model/create/')
        self.assertEqual(response.status_code, 200)
        # TODO Add better error message

    # Delete dialog
    def test_delete_dialog(self):
        response = self.client.get(self.get_user_url(self.test_user.id, action='delete'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.test_user.email)

    def test_post_delete_dialog(self):
        response = self.client.post(self.get_user_url(self.test_user.id, action='delete'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"success": true')
        self.assertEqual(User.objects.count(), 1)

    def test_404_delete_dialog(self):
        response = self.client.get(self.get_user_url(9999, action='delete'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Could not load')
