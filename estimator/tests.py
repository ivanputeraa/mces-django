from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client

# Create your tests here.

class LoginTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='dummy user')
        user.set_password('dummy password')
        user.save()
        pass

    def setUp(self):
        pass

    def test_login_success(self):
        c = Client()
        logged_in = c.login(username='dummy user', password='dummy password')

        self.assertTrue(logged_in, "Login Succeed")

    def test_login_failed(self):
        c = Client()
        logged_in = c.login(username='real user', password='dummy password')

        self.assertFalse(logged_in, "Login Failed")

    def test_login_with_null_username(self):
        c = Client()
        logged_in = c.login(username='', password='dummy password')

        self.assertFalse(logged_in, "Login Failed")

    def test_login_with_null_password(self):
        c = Client()
        logged_in = c.login(username='dummy user', password='')

        self.assertFalse(logged_in, "Login Failed")

    def test_login_with_both_fields_null(self):
        c = Client()
        logged_in = c.login(username='', password='')

        self.assertFalse(logged_in, "Login Failed")