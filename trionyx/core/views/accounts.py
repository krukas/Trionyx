from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth import logout as django_logout
from django.shortcuts import redirect
from django.urls import reverse
from .core import UpdateView, DetailTabView

from trionyx.core.models import User
from trionyx.core.forms.accounts import UserUpdateForm

class LoginView(DjangoLoginView):
    template_name = 'trionyx/core/login.html'


def logout(request):
    django_logout(request)
    return redirect('/')


class UpdateUserAccountView(UpdateView):
    model = User
    form_class = UserUpdateForm
    title = 'Update account'

    def get(self, request, *args, **kwargs):
        kwargs['pk'] = request.user.id
        self.kwargs['pk'] = request.user.id
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        kwargs['pk'] = request.user.id
        self.kwargs['pk'] = request.user.id
        return super().post(request, *args, **kwargs)


class ViewUserAccountView(DetailTabView):
    model_alias = 'core.profile'
    model = User

    title = 'Profile'

    def get(self, request, *args, **kwargs):
        kwargs['pk'] = request.user.id
        self.kwargs['pk'] = request.user.id
        return super().get(request, *args, **kwargs)

    def get_edit_url(self):
        return reverse('trionyx:edit-account')