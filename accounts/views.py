import requests
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

def login(request):
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"  
        "&client_id={client_id}"
        "&redirect_uri={redirect_uri}"
        "&scope=email%20openid%20profile"
        "&access_type=offline"  # Это важно для получения refresh токена
        "&prompt=consent"       # Это важно для повторного запроса refresh токена
    ).format(
        client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
        redirect_uri="http://localhost:8000/accounts/complete/google-oauth2/"
    )
    return redirect(google_auth_url)

def callback(request):
    code = request.GET.get('code')  # Получите код авторизации
    if not code:
        return JsonResponse({'error': 'Authorization code is missing'}, status=400)

    # Обменяйте код на access_token и refresh_token
    token_response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            'code': code,
            'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
            'redirect_uri': "http://localhost:8000/accounts/complete/google-oauth2/",
            'grant_type': 'authorization_code'
        }
    )

    token_data = token_response.json()
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')

    if not access_token:
        return JsonResponse({'error': 'Access token is missing'}, status=400)

    # Запрос информации о пользователе
    user_info_response = requests.get(
        'https://www.googleapis.com/oauth2/v1/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    user_info = user_info_response.json()

    # Возвращаем email, access_token и refresh_token
    return JsonResponse({
        'email': user_info.get('email'), 
        'access_token': access_token,  # Добавлено
        'refresh_token': refresh_token
    })

def refresh_access_token(refresh_token):
    response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
    )
    return response.json()

@require_GET
@csrf_exempt
def protected_view(request):
    if hasattr(request, 'user_email'):
        return JsonResponse({'message': 'This is a protected view', 'email': request.user_email})
    return JsonResponse({'error': 'Unauthorized'}, status=401)
