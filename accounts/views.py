import requests
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from django.views.decorators.csrf import csrf_exempt

def login(request):
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=token"
        "&client_id={client_id}"
        "&redirect_uri={redirect_uri}"
        "&scope=email"
    ).format(
        client_id=settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
        redirect_uri="http://localhost:8000/accounts/complete/google-oauth2/"
    )
    return redirect(google_auth_url)

def callback(request):
    token = request.GET.get('access_token')
    if not token:
        return JsonResponse({'error': 'Token is missing'}, status=400)

    try:
        # Валидация токена
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY)
        email = idinfo['email']
        # Дополнительные действия (например, создание пользователя в БД)
        return JsonResponse({'email': email})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.conf import settings

@require_GET
@csrf_exempt
def protected_view(request):
    if hasattr(request, 'user_email'):
        # Здесь вы можете использовать email пользователя, чтобы выполнять действия, например:
        return JsonResponse({'message': 'This is a protected view', 'email': request.user_email})
    return JsonResponse({'error': 'Unauthorized'}, status=401)