import json
import requests
from django.http import JsonResponse
from django.conf import settings

class GoogleAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token:
            token = token.split(' ')[1]  # Предполагается, что токен передается как "Bearer <token>"
            try:
                # Запрос к Google API для проверки access token
                response = requests.get(f'https://oauth2.googleapis.com/tokeninfo?access_token={token}')
                idinfo = response.json()

                if 'error' in idinfo:
                    print(f"Token validation error: {idinfo['error']}")  # Выводим ошибку для отладки
                    return JsonResponse({'error': 'Invalid token'}, status=401)

                # Проверяем, что токен действителен и получаем email
                request.user_email = idinfo['email']  # Сохранение email в запросе для дальнейшего использования

            except Exception as e:
                print(f"Token validation error: {e}")  # Выводим ошибку для отладки
                return JsonResponse({'error': 'Invalid token'}, status=401)

        response = self.get_response(request)
        return response
