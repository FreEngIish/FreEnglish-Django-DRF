import responses
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from django.contrib.auth.models import AnonymousUser

class GoogleAuthMiddlewareTests(APITestCase):

    def create_user(self, email='test@example.com'):
        return User.objects.create_user(email=email, password='password', google_sub='google_unique_id')

    @responses.activate
    def test_valid_token(self):
        # Создание пользователя
        user = self.create_user()

        # Мок ответа Google OAuth с валидным токеном
        responses.add(
            responses.GET,
            'https://oauth2.googleapis.com/tokeninfo?access_token=valid_token',
            json={
                'email': user.email,
                'expires_in': 3600,
            },
            status=200
        )

        # Отправляем запрос с валидным токеном
        response = self.client.get(reverse('protected'), HTTP_AUTHORIZATION='Bearer valid_token')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.wsgi_request.user.email, user.email)

    @responses.activate
    def test_invalid_token(self):
        # Мок ответа Google OAuth с невалидным токеном
        responses.add(
            responses.GET,
            'https://oauth2.googleapis.com/tokeninfo?access_token=invalid_token',
            json={'error': 'Invalid token'},
            status=401
        )

        # Отправляем запрос с невалидным токеном
        response = self.client.get(reverse('protected'), HTTP_AUTHORIZATION='Bearer invalid_token')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json(), {'error': 'Invalid token'})

    @responses.activate
    def test_no_token(self):
        # Запрос без токена
        response = self.client.get(reverse('protected'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(isinstance(response.wsgi_request.user, AnonymousUser))
