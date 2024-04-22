from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from cinema.factory import UserFactory

User = get_user_model()


class AuthTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_login(self):
        url = reverse('login_page')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = {
            'username': 'Rose',
            'password': 'rose1234_',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        self.client.login(
            username='Rose',
            password='rose1234_'
        )

        url = reverse('logout_page')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url, reverse('schedule_page'))

    def test_signup(self):
        url = reverse('signup_page')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = {
            'username': 'Johny',
            'email': 'johny@gmail.com',
            'password1': 'johny_1234',
            'password2': 'johny_1234',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url, reverse('schedule_page'))

        user = User.objects.get(username='Johny')
        self.assertIsNotNone(user)
