from .base import *  # noqa: F403
from decouple import config
from rest_framework import permissions

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

SWAGGER_SETTINGS = {
    'DEFAULT_INFO': 'my_project.urls.swagger_info',
    'USE_SESSION_AUTH': True,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
        },
    },
    'DEFAULT_AUTO_SCHEMA_CLASS': 'drf_yasg.inspectors.SwaggerAutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_PERMISSIONS': [permissions.AllowAny],
}
