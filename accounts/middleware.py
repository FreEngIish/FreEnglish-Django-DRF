import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse


class GoogleAuthMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')

        if token:
            token = token.split(' ')[1]
            try:
                response = requests.get(f'https://oauth2.googleapis.com/tokeninfo?access_token={token}')
                idinfo = response.json()

                if 'error' in idinfo:
                    return JsonResponse({'error': 'Invalid token'}, status=401)

                user_email = idinfo['email']
                request.user_email = user_email

                User = get_user_model()
                try:
                    user = User.objects.get(email=user_email)
                    request.user = user
                except User.DoesNotExist:
                    request.user = AnonymousUser()

            except Exception:
                return JsonResponse({'error': 'Invalid token'}, status=401)
        else:
            request.user = AnonymousUser()

        response = self.get_response(request)
        return response
