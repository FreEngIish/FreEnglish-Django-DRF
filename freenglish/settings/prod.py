from .base import *

DEBUG = False

ALLOWED_HOSTS = ['production_domain.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', '5432'),
    }
}

LOGIN_REDIRECT_URL = 'http://production_domain.com/accounts/complete/google-oauth2/'
LOGOUT_REDIRECT_URL = 'http://production_domain.com/accounts/complete/google-oauth2/'

CSRF_TRUSTED_ORIGINS = [
    'http://production_domain.com'
]
