import responses
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from django.contrib.auth.models import AnonymousUser
from django.views.decorators.csrf import csrf_exempt

class GoogleAuthMiddlewareTests(APITestCase):

    def create_user(self, email='test@example.com'):
        return User.objects.create_user(email=email, password='password', google_sub='google_unique_id')

    @responses.activate
    def test_valid_token(self):
        user = self.create_user()

        responses.add(
            responses.GET,
            'https://oauth2.googleapis.com/tokeninfo?access_token=valid_token',
            json={
                'email': user.email,
                'expires_in': 3600,
            },
            status=200
        )

        response = self.client.get(reverse('protected'), HTTP_AUTHORIZATION='Bearer valid_token')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.wsgi_request.user.email, user.email)

    @responses.activate
    def test_invalid_token(self):
        responses.add(
            responses.GET,
            'https://oauth2.googleapis.com/tokeninfo?access_token=invalid_token',
            json={'error': 'Invalid token'},
            status=401
        )

        response = self.client.get(reverse('protected'), HTTP_AUTHORIZATION='Bearer invalid_token')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json(), {'error': 'Invalid token'})

    @responses.activate
    def test_no_token(self):
        response = self.client.get(reverse('protected'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(isinstance(response.wsgi_request.user, AnonymousUser))

import responses
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken

class GoogleAuthEndpointsTests(APITestCase):

    def create_user(self, email='test@example.com'):
        return User.objects.create_user(email=email, password='password', google_sub='google_unique_id')

    @responses.activate
    def test_callback_with_missing_code(self):
        user = self.create_user()
        self.client.force_authenticate(user=user)
        response = self.client.get(reverse('callback'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @responses.activate
    def test_callback_with_valid_code(self):
        responses.add(
            responses.POST,
            'https://oauth2.googleapis.com/token',
            json={'access_token': 'new_access_token', 'refresh_token': 'new_refresh_token'},
            status=200
        )

        responses.add(
            responses.GET,
            'https://www.googleapis.com/oauth2/v1/userinfo',
            json={'email': 'test@example.com', 'id': 'google_unique_id'},
            status=200
        )

        user = self.create_user()
        self.client.force_authenticate(user=user)

        response = self.client.get(reverse('callback'), {'code': 'valid_code'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    @responses.activate
    def test_refresh_access_token(self):
        responses.add(
            responses.POST,
            'https://oauth2.googleapis.com/token',
            json={'access_token': 'new_access_token', 'expires_in': 3600},
            status=200
        )

        user = self.create_user()
        self.client.force_authenticate(user=user)

        response = self.client.post(reverse('refresh_access_token'), data={'refresh_token': 'valid_refresh_token'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @responses.activate
    def test_refresh_access_token_with_invalid_token(self):
        responses.add(
            responses.POST,
            'https://oauth2.googleapis.com/token',
            json={'error': 'invalid_grant'},
            status=400
        )

        user = self.create_user()
        self.client.force_authenticate(user=user)

        response = self.client.post(reverse('refresh_access_token'), data={'refresh_token': 'invalid_refresh_token'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
