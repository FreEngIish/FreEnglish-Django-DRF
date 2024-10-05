from .base import *  # noqa: F403


DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),  # noqa: F405
    }
}


LOGIN_REDIRECT_URL = 'http://localhost:8000/accounts/complete/google-oauth2/'
LOGOUT_REDIRECT_URL = 'http://localhost:8000/accounts/complete/google-oauth2/'

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000'
]
