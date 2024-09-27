import requests
from django.http import JsonResponse


class GoogleAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token:
            token = token.split(' ')[1]  # It is assumed that the token is passed as "Bearer <token>"
            try:
                # Request to Google API to verify the access token
                response = requests.get(f'https://oauth2.googleapis.com/tokeninfo?access_token={token}')
                idinfo = response.json()

                if 'error' in idinfo:
                    return JsonResponse({'error': 'Invalid token'}, status=401)

                # Check that the token is valid and get the email
                request.user_email = idinfo['email']  # Save email in the request for later use

            except Exception:
                return JsonResponse({'error': 'Invalid token'}, status=401)

        response = self.get_response(request)
        return response
