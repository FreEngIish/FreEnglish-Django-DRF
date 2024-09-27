from django.urls import include, path

from . import views


urlpatterns = [
    # Include social authentication URLs from social_django package
    path('auth/', include('social_django.urls', namespace='social')),

    # Route for Google login
    path('login/google/', views.login, name='google_login'),

    # Callback route to handle the response from Google after authentication
    path('complete/google-oauth2/', views.callback, name='callback'),

    # Protected route for test access token valid. This is temporary.
    path('protected/', views.protected_view, name='protected'),

    # Route to refresh the access token using the refresh token
    path('refresh-token/', views.refresh_access_token_view, name='refresh_access_token'),

    # Temporary route to obtain CSRF token; this is a workaround until Swagger is implemented
    path('csrf-token/', views.get_csrf_token, name='get_csrf_token'),
]
