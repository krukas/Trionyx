"""
trionyx.trionyx.view.accounts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from collections import OrderedDict

from django.http import HttpResponse
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth import logout as django_logout
from django.shortcuts import redirect
from django.urls import reverse
from django_jsend import JsendView
from watson import search as watson
from django.contrib.contenttypes.models import ContentType

from trionyx.views import UpdateView, DetailTabView
from trionyx.trionyx.models import User
from trionyx.config import models_config


def media_nginx_accel(request, path):
    """
    Location /protected/ {
        internal;
        root <complete path to project root dir>;
    }

    """
    response = HttpResponse(status=200)
    response['Content-Type'] = ''
    response['X-Accel-Redirect'] = '/protected' + request.path
    return response


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
    title = 'Update account'
    cancel_url = 'trionyx:view-account'

    @property
    def form_class(self):
        """Form class used by view"""
        from trionyx.trionyx.forms import ProfileUpdateForm
        return ProfileUpdateForm

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


# =============================================================================
# Global search
# =============================================================================
class GlobalSearchJsendView(JsendView):
    """View for global search uses watson to search all models"""

    def handle_request(self, request):
        """Handle search"""
        models = []
        content_types = {}
        for config in models_config.get_all_configs(False):
            if config.disable_search_index or not config.global_search:
                continue

            # Check if user has view permission
            if not request.user.has_perm('{app_label}.view_{model_name}'.format(
                app_label=config.app_label,
                model_name=config.model_name,
            ).lower()):
                continue

            models.append(config.model)
            content_type = ContentType.objects.get_for_model(config.model, False)
            content_types[content_type.id] = str(config.model._meta.verbose_name_plural)

        results = OrderedDict()
        for entry in watson.search(request.GET.get('search', ''), models=models)[:100]:
            if entry.content_type_id not in results:
                results[entry.content_type_id] = {
                    'name': content_types[entry.content_type_id],
                    'items': [],
                }

            if len(results[entry.content_type_id]['items']) <= 10:
                results[entry.content_type_id]['items'].append({
                    'url': entry.url,
                    'title': entry.title,
                    'description': entry.description,
                })

        return list(results.values())
