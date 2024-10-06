from .base import *  # noqa: F403
from decouple import config

DEPLOY_URL = config('DEPLOY_URL', default='symmetrical-computing-machine-5rpjw5rrgv4247x4.github.dev')
DEPLOY_URL_ONLY_FOR_GITHUB = config('DEPLOY_URL_ONLY_FOR_GITHUB', default='https://symmetrical-computing-machine-5rpjw5rrgv4247x4-8000.app.github.dev')

DEBUG = config('DEBUG', default='True', cast=bool)

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    DEPLOY_URL,
    f"{DEPLOY_URL}:8001"
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),  # noqa: F405
    }
}

LOGIN_REDIRECT_URL = config('LOGIN_REDIRECT_URL', default=f"{DEPLOY_URL_ONLY_FOR_GITHUB}/accounts/complete/google-oauth2/")
LOGOUT_REDIRECT_URL = config('LOGOUT_REDIRECT_URL', default=f"{DEPLOY_URL_ONLY_FOR_GITHUB}/accounts/complete/google-oauth2/")

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    DEPLOY_URL_ONLY_FOR_GITHUB
]
