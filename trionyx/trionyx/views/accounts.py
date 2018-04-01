"""
trionyx.trionyx.view.accounts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth import logout as django_logout
from django.shortcuts import redirect
from django.urls import reverse
from .core import UpdateView, DetailTabView

from trionyx.trionyx.models import User
from trionyx.trionyx.forms.accounts import UserUpdateForm


class LoginView(DjangoLoginView):
    """Trionyx login view"""

    template_name = 'trionyx/core/login.html'


def logout(request):
    """Trionyx logout view"""
    django_logout(request)
    return redirect('/')


class UpdateUserAccountView(UpdateView):
    """Update user view"""

    model = User
    form_class = UserUpdateForm
    title = 'Update account'
    cancel_url = 'trionyx:view-account'

    def get(self, request, *args, **kwargs):
        """Add user id to kwargs"""
        kwargs['pk'] = request.user.id
        self.kwargs['pk'] = request.user.id
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Add user id to kwargs"""
        kwargs['pk'] = request.user.id
        self.kwargs['pk'] = request.user.id
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        """Set success url to account page"""
        return reverse('trionyx:view-account')


class ViewUserAccountView(DetailTabView):
    """View user"""

    model_alias = 'trionyx.profile'
    model = User

    title = 'Profile'

    def get(self, request, *args, **kwargs):
        """Add user id to kwargs"""
        kwargs['pk'] = request.user.id
        self.kwargs['pk'] = request.user.id
        return super().get(request, *args, **kwargs)

    def get_edit_url(self):
        """Get user edit url"""
        return reverse('trionyx:edit-account')

    def get_delete_url(self):
        """Hide delete url"""
        return None

    def get_back_url(self):
        """Hide back url"""
        return None
