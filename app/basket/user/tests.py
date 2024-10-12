from django.test import TestCase, Client
from django.urls import reverse

# Create your tests here.


class tests(TestCase):
    def setUp(self):
        self.client = Client()

    #registration tests

    #test that validation for secure passwords work
    def test_password_strength(self):
        response = self.client.post(reverse('register'), {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': '123',  # Weak password
            'confirm_password': '123'
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error'], "Password has to be at least 10 charactes long")