# views.py

from django.shortcuts import redirect


def google_login(request):  # noqa: ARG001
    return redirect('social:begin', 'google-oauth2')
