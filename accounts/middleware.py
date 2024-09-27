import requests
from django.http import JsonResponse


class GoogleAuthMiddleware:
    """
    Middleware to authenticate requests using Google OAuth 2.0 access tokens.

    This middleware extracts the Bearer token from the Authorization header,
    verifies it with the Google API, and retrieves the associated user email.
    If the token is valid, the email is added to the request object for later use.

    Attributes:
        get_response: The next middleware or view in the request-response cycle.
    """

    def __init__(self, get_response):
        """
        Initializes the middleware with the next response handler.

        Args:
            get_response: The next middleware or view to be called in the chain.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Processes the incoming request, verifies the access token if present,
        and attaches the user email to the request.

        Args:
            request: The HTTP request object containing the incoming request data.

        Returns:
            HttpResponse: The response from the next middleware or view in the chain,
            which may be modified if the token is invalid.
        """
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
