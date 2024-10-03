import json

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view

from .services import UserService


user_service = UserService()

def login(request):  # noqa: ARG001
    """
    Initiates the OAuth 2.0 login process by redirecting the user to the Google
    authentication URL. The URL includes necessary parameters for obtaining
    authorization, including client ID and redirect URI.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects the user to the Google OAuth 2.0 login page.
    """
    google_auth_url = (
        'https://accounts.google.com/o/oauth2/v2/auth'
        '?response_type=code'
        '&client_id={client_id}'
        '&redirect_uri={redirect_uri}'
        '&scope=email%20openid%20profile'
        '&access_type=offline'  # Important for obtaining a refresh token
        '&prompt=consent'       # Important for re-requesting the refresh token
    ).format(
        client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
        redirect_uri='http://localhost:8000/accounts/complete/google-oauth2/'
    )
    return redirect(google_auth_url)

def callback(request):
    code = request.GET.get('code')
    if not code:
        return JsonResponse({'error': 'Authorization code is missing'}, status=400)

    token_response = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'code': code,
            'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
            'redirect_uri': 'http://localhost:8000/accounts/complete/google-oauth2/',
            'grant_type': 'authorization_code'
        }
    )

    token_data = token_response.json()
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')

    if not access_token:
        return JsonResponse({'error': 'Access token is missing'}, status=400)

    user_info_response = requests.get(
        'https://www.googleapis.com/oauth2/v1/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    user_info = user_info_response.json()
    email = user_info.get('email')
    google_sub = user_info.get('id')

    # Save user to the database through the service
    user, created = user_service.get_or_create_user(google_sub, email, user_info)

    if created:
        user.set_unusable_password()  # Set unusable password for users
        user.save()

    return JsonResponse({
        'email': email,
        'google_sub': google_sub,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'avatar': user_info.get('picture', ''),
        'locale': user_info.get('locale', ''),
    })

@require_POST
def refresh_access_token_view(request):
    """
    Endpoint to refresh the access token using the provided refresh token.
    It parses the incoming request, verifies the refresh token, and returns
    a new access token and its expiration time.

    Args:
        request: The HTTP request object containing the refresh token in JSON format.

    Returns:
        JsonResponse: Contains the new access token and its expiration time or an
        error message if the refresh token is invalid or missing.
    """
    try:
        body = json.loads(request.body)  # Load the request body
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    refresh_token = body.get('refresh_token')  # Get the refresh_token
    if not refresh_token:
        return JsonResponse({'error': 'Refresh token is missing'}, status=400)

    response = refresh_access_token(refresh_token)
    if 'error' in response:
        return JsonResponse({'error': response['error']}, status=400)

    return JsonResponse({
        'access_token': response.get('access_token'),
        'expires_in': response.get('expires_in')
    })

def refresh_access_token(refresh_token):
    """
    Requests a new access token using the provided refresh token.

    Args:
        refresh_token (str): The refresh token to exchange for a new access token.

    Returns:
        dict: The response containing the new access token and its expiration
        time or an error message.
    """
    response = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
    )
    return response.json()

@require_GET
def protected_view(request):
    """
    A protected view that requires authentication. It checks if the user is
    authenticated and returns a success message along with the user's email.

    Args:
        request: The HTTP request object.

    Returns:
        JsonResponse: Contains a success message and user email if authenticated,
        or an error message if unauthorized.
    """
    if hasattr(request, 'user_email'):
        return JsonResponse({'message': 'This is a protected view', 'email': request.user_email})
    return JsonResponse({'error': 'Unauthorized'}, status=401)

@csrf_exempt
def get_csrf_token(request):
    """
    Provides a CSRF token for AJAX requests. This is a temporary endpoint
    for testing purposes.

    Args:
        request: The HTTP request object.

    Returns:
        JsonResponse: Contains the CSRF token for the client to use.
    """
    return JsonResponse({'csrf_token': request.META.get('CSRF_COOKIE')})


@swagger_auto_schema(
    method='get',
    operation_description="Получает информацию о текущем пользователе, включая username и date_joined.",
    responses={
        200: openapi.Response(
            description="User information",
            examples={
                "application/json": {
                    "email": "user@example.com",
                    "username": "user123",
                    "first_name": "John",
                    "last_name": "Doe",
                    "avatar": "https://example.com/avatar.jpg",
                    "locale": "en-US",
                    "date_joined": "2024-10-03 12:34:56"
                }
            }
        )
    }
)
@api_view(['GET'])
@login_required
def get_user_info(request):
    """
    Получает информацию о текущем пользователе, включая username и date_joined.
    Декоратор login_required требует авторизации для доступа к этому представлению.
    """
    user = request.user
    return JsonResponse({
        'email': user.email,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'avatar': user.avatar,
        'locale': user.locale,
        'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S')
    })

@swagger_auto_schema(
    method='patch',
    operation_description="Обновляет информацию о текущем пользователе: avatar, locale, first_name, last_name.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'avatar': openapi.Schema(type=openapi.TYPE_STRING, description='URL аватара пользователя'),
            'locale': openapi.Schema(type=openapi.TYPE_STRING, description='Локаль пользователя'),
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Имя пользователя'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Фамилия пользователя')
        }
    ),
    responses={
        200: openapi.Response(
            description="User updated successfully",
            examples={
                "application/json": {
                    "message": "User updated successfully",
                    "first_name": "John",
                    "last_name": "Doe",
                    "avatar": "https://example.com/avatar.jpg",
                    "locale": "en-US"
                }
            }
        )
    }
)
@api_view(['PATCH'])
@csrf_exempt
@login_required
def update_user_info(request):
    """
    Обновляет информацию о текущем пользователе: avatar, locale, first_name, last_name.
    Обновление происходит частично (PATCH).
    """
    if request.method == 'PATCH':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        user = request.user

        if 'avatar' in data:
            user.avatar = data['avatar']
        if 'locale' in data:
            user.locale = data['locale']
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']

        user.save()

        return JsonResponse({
            'message': 'User updated successfully',
            'first_name': user.first_name,
            'last_name': user.last_name,
            'avatar': user.avatar,
            'locale': user.locale
        })

    return JsonResponse({'error': 'Invalid request method'}, status=405)


User = get_user_model()

@swagger_auto_schema(
    method='delete',
    operation_description="Удаляет текущего пользователя.",
    responses={
        200: openapi.Response(
            description="User deleted successfully",
            examples={
                "application/json": {
                    "message": "User deleted successfully"
                }
            }
        )
    }
)
@api_view(['DELETE'])
@csrf_exempt
@login_required
def delete_user(request):
    """
    Удаляет текущего пользователя.
    """
    user = request.user
    user.delete()
    return JsonResponse({'message': 'User deleted successfully'})
