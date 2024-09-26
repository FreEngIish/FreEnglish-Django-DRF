from django.urls import include, path

from . import views


urlpatterns = [
    path('auth/', include('social_django.urls', namespace='social')),
    path('login/google/', views.google_login, name='google_login'),
]
