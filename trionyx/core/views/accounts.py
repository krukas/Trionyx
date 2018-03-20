from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth import logout as django_logout
from django.shortcuts import redirect


class LoginView(DjangoLoginView):
    template_name = 'trionyx/core/login.html'


def logout(request):
    django_logout(request)
    return redirect('/')