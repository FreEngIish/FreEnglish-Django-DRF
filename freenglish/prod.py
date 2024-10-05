from .base import *  # noqa: F403


DEBUG = False

ALLOWED_HOSTS = ['production_domain.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),  # noqa: F405
        'USER': config('DB_USER'),  # noqa: F405
        'PASSWORD': config('DB_PASSWORD'),  # noqa: F405
        'HOST': config('DB_HOST'),  # noqa: F405
        'PORT': config('DB_PORT', '5432'),  # noqa: F405
    }
}

LOGIN_REDIRECT_URL = 'http://production_domain.com/accounts/complete/google-oauth2/'
LOGOUT_REDIRECT_URL = 'http://production_domain.com/accounts/complete/google-oauth2/'

CSRF_TRUSTED_ORIGINS = [
    'http://production_domain.com'
]
