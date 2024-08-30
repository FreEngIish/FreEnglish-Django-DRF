import requests
from django.conf import settings
from django.contrib.auth import (
    login,
    logout as django_logout,
)
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import redirect

from .utils import save_user_to_db  # Function for saving user


def login_redirect(request):  # noqa: ARG001
    # URL for redirecting to the Auth0 login page with required query parameters
    auth0_url = (
        f'https://{settings.AUTH0_DOMAIN}/authorize?'
        f'audience={settings.API_IDENTIFIER}&'  # API audience to which the access token should be valid
        f'response_type=code&'  # Authorization code flow
        f'client_id={settings.SOCIAL_AUTH_AUTH0_KEY}&'  # Client ID for the Auth0 application
        f'redirect_uri={settings.AUTH0_CALLBACK_URL}&'  # URI to which Auth0 will redirect after login
        f'scope=openid profile email'  # Scopes to request from Auth0
    )
    return redirect(auth0_url)

def auth0_callback(request):
    code = request.GET.get('code')

    if not code:
        return HttpResponseBadRequest('Authorization code is missing.')

    try:
        token_url = f'https://{settings.AUTH0_DOMAIN}/oauth/token'
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': settings.SOCIAL_AUTH_AUTH0_KEY,
            'client_secret': settings.SOCIAL_AUTH_AUTH0_SECRET,
            'code': code,
            'redirect_uri': settings.AUTH0_CALLBACK_URL,
        }
        token_headers = {'Content-Type': 'application/json'}
        token_response = requests.post(token_url, json=token_data, headers=token_headers)

        if token_response.status_code != 200:
            return HttpResponseServerError(f'Failed to get tokens: {token_response.text}')

        tokens = token_response.json()
        id_token = tokens.get('id_token')
        access_token = tokens.get('access_token')

        if not id_token or not access_token:
            return HttpResponseServerError('Failed to retrieve tokens from response.')

        # Save the user and handle login
        user = save_user_to_db(id_token)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        # Save the access token in an HttpOnly cookie for security
        response = HttpResponse('Authentication successful')
        response.set_cookie('access_token', access_token, httponly=True, secure=True)

        return response

    except requests.RequestException as e:
        return HttpResponseServerError(f'Network error occurred: {str(e)}')

    except ValueError as e:
        return HttpResponseServerError(f'Token error: {str(e)}')

    except Exception as e:
        return HttpResponseServerError(f'An unexpected error occurred: {str(e)}')

def logout(request):
    # End the user's session in Django
    django_logout(request)

    # Create a response and redirect to Auth0 logout URL
    # Also remove the access_token from Cookies
    response = redirect(f'https://{settings.AUTH0_DOMAIN}/v2/logout?client_id={settings.SOCIAL_AUTH_AUTH0_KEY}&returnTo={settings.LOGOUT_REDIRECT_URL}')
    response.delete_cookie('access_token')

    return response
