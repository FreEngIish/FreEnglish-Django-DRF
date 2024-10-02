from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from accounts.models import User
from tests.utils_test import create_test_google_token

class GoogleAuthTests(APITestCase):

    def create_user(self, email='test@example.com', password='password'):
        return User.objects.create_user(email=email, password=password, google_sub='google_unique_id')  # Добавлен google_sub

    @patch('accounts.views.requests.post')
    @patch('accounts.views.requests.get')
    def test_callback_success(self, mock_get, mock_post):
        mock_post.return_value.json.return_value = {
            'access_token': 'mock_access_token',
            'refresh_token': 'mock_refresh_token',
        }
        
        mock_get.return_value.json.return_value = {
            'email': 'test@example.com',
            'id': 'mock_google_id',
        }
        
        response = self.client.get(reverse('callback'), {'code': 'mock_code'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.json())
        self.assertIn('refresh_token', response.json())

    @patch('accounts.views.requests.post')
    def test_callback_missing_code(self, mock_post):
        response = self.client.get(reverse('callback'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'Authorization code is missing'})

    @patch('accounts.views.requests.post')
    @patch('accounts.views.requests.get')
    def test_refresh_access_token_success(self, mock_get, mock_post):
        mock_post.return_value.json.return_value = {
            'access_token': 'new_access_token',
            'expires_in': 3600,
        }
        mock_post.return_value.status_code = 200

        response = self.client.post(reverse('refresh_access_token'), {'refresh_token': 'mock_refresh_token'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.json())

    def test_refresh_access_token_missing(self):
        response = self.client.post(reverse('refresh_access_token'), {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'Refresh token is missing'})
