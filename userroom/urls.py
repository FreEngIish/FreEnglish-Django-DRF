from django.urls import path

from .views import auth0_callback, login_redirect, logout


urlpatterns = [
    path('login/', login_redirect, name='login_redirect'),
    path('logout/', logout, name='logout'),
    path('callback/', auth0_callback, name='auth0_callback'),
]
