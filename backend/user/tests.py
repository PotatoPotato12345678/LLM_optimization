from django.test import TestCase, Client
from .models import User
from django.urls import reverse
import json as pyjson

class UserAuthTests(TestCase):
    def setUp(self):
        # Create a test user with properly hashed password
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass', 
            is_manager=True
        )
        self.client = Client()
        self.url = reverse('user')

    def login_user(self, username='testuser', password='testpass'):
        """Helper to log in the user via POST"""
        return self.client.post(
            self.url,
            data=pyjson.dumps({'username': username, 'password': password}),
            content_type='application/json'
        )

    def test_post_login_success(self):
        from django.test import TestCase, Client
        from .models import User
        from django.urls import reverse
        import json as pyjson


        class UserAuthTests(TestCase):
            def setUp(self):
                # Create a test user with properly hashed password
                self.user = User.objects.create_user(
                    username='testuser', 
                    password='testpass', 
                    is_manager=True
                )
                self.client = Client()
                self.url = reverse('user')

            def login_user(self, username='testuser', password='testpass'):
                """Helper to log in the user via POST"""
                return self.client.post(
                    self.url,
                    data=pyjson.dumps({'username': username, 'password': password}),
                    content_type='application/json'
                )

            def test_post_login_success(self):
                response = self.login_user()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()['message'], 'Login successful')

            def test_post_login_failure(self):
                response = self.login_user(password='wrongpass')
                self.assertEqual(response.status_code, 404)
                self.assertEqual(response.json()['error'], 'Not Found')

            def test_post_invalid_data(self):
                response = self.client.post(
                    self.url,
                    data='invalid json',
                    content_type='application/json'
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json()['error'], 'Invalid data')

            def test_get_requires_login(self):
                # Without login, should redirect (302)
                response = self.client.get(self.url)
                self.assertEqual(response.status_code, 302)

                # Log in via POST first - this should maintain the session
                login_response = self.login_user()
                self.assertEqual(login_response.status_code, 200)
        
                # Now GET should work with the same client instance
                response = self.client.get(self.url)
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data['username'], 'testuser')
                self.assertTrue(data['is_manager'])

            def test_delete_requires_login(self):
                # Without login
                response = self.client.delete(self.url)
                self.assertEqual(response.status_code, 302)

                # Log in first - this should maintain the session
                login_response = self.login_user()
                self.assertEqual(login_response.status_code, 200)
        
                # Now DELETE should work with the same client instance
                response = self.client.delete(self.url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()['message'], 'Logout successful')
