from django.urls import include, path

from . import views


urlpatterns = [
    path('auth/', include('social_django.urls', namespace='social')),
    path('login/google/', views.login, name='google_login'),
    path('complete/google-oauth2/', views.callback, name='callback'),
    path('protected/', views.protected_view, name='protected'),
    path('refresh-token/', views.refresh_access_token_view, name='refresh_access_token'),  # Новый маршрут
    #This is temporary route because we don't have a swagger. Don't pay attention
    path('csrf-token/', views.get_csrf_token, name='get_csrf_token'),
]
