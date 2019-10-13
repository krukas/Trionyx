"""
trionyx.trionyx.view.accounts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import json
import logging
from collections import OrderedDict

from django.http import HttpResponse
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth import logout as django_logout
from django.shortcuts import redirect
from django.urls import reverse
from django_jsend import JsendView
from watson import search as watson
from django.contrib.contenttypes.models import ContentType
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static

from trionyx.views import UpdateView, DetailTabView, DialogView
from trionyx.trionyx.models import User
from trionyx.config import models_config
from trionyx.widgets import widgets
from trionyx import utils
from trionyx.forms.helper import FormHelper

logger = logging.getLogger(__name__)


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


class FilterFieldsJsendView(JsendView):
    """View for getting model filter fields"""

    def handle_request(self, request, *args, **kwargs):
        """Get filter fields"""
        from trionyx.urls import model_url

        modelClass = ContentType.objects.get_for_id(request.GET.get('id')).model_class()
        config = models_config.get_config(modelClass)

        return {
            'id': request.GET.get('id'),
            'choices_url': model_url(config.model, 'list-choices'),
            'fields': {
                name: {
                    'name': name,
                    'label': str(field['label']),
                    'type': field['type'],
                    'choices': field['choices'],
                }
                for name, field in config.get_list_fields().items()
            }
        }

# =============================================================================
# Dashboard
# =============================================================================
class DashboardView(TemplateView):
    """Dashboard view"""

    template_name = 'trionyx/core/dashboard.html'

    def get_context_data(self, *args, **kwargs):
        """Get dashboard context data"""
        context = super().get_context_data(*args, ** kwargs)
        dashboard = self.request.user.get_attribute('tx_dashboard', [])
        if not dashboard:
            for widget in settings.TX_DEFAULT_DASHBOARD:
                widget = widget.copy()
                widget['i'] = utils.random_string(16)
                dashboard.append(widget)

            self.request.user.set_attribute('tx_dashboard', dashboard)

        context.update({
            'widget_templates': [widget().template for index, widget in widgets.items()],
            'widgets': [{
                'code': widget.code,
                'name': widget.name,
                'description': widget.description,
                'image': static(widget().image),
                'config_fields': widget().config_fields,
                'default_w': widget.default_width,
                'default_h': widget.default_height,
            } for index, widget in widgets.items()],
            'dashboard': dashboard,
        })
        return context


class WidgetDataJsendView(JsendView):
    """Jsend view to get widget data"""

    def handle_request(self, request):
        """Get widget data"""
        data = json.loads(request.body.decode('utf-8'))

        if data['code'] not in widgets:
            raise Exception('Widget does not exists')

        widget = widgets.get(data['code'])()

        return widget.get_data(request, data.get('config', {}))


class SaveDashboardJsendView(JsendView):
    """Jsend view to save user dashboard"""

    def handle_request(self, request):
        """Handle dashboard save"""
        dashboard = json.loads(request.body.decode('utf-8'))

        if not isinstance(dashboard, list):
            raise Exception('Expect dashboard to be a list')

        request.user.set_attribute('tx_dashboard', dashboard)

        return 'saved'


class WidgetConfigDialog(DialogView):
    """Widget config dialog view"""

    def display_dialog(self, code, *args, **kwargs):
        """Handle widget config"""
        if code not in widgets:
            raise Exception('Widget does not exists')

        if '__post__' in self.request.POST:
            post = self.request.POST
            initial = None
        else:
            post = None
            initial = self.request.POST

        widget = widgets.get(code)
        form = widget.config_form_class(post, initial=initial) if widget.config_form_class else None

        config = None
        if form:
            if not hasattr(form, "helper"):
                form.helper = FormHelper(form)
            form.helper.form_tag = False

            if form.is_valid():
                config = form.cleaned_data
                config['title'] = self.request.POST.get('title')
                config['refresh'] = self.request.POST.get('refresh')
            else:
                logger.error(json.dumps(form.errors))
        elif '__post__' in self.request.POST:
            config = {
                'title': self.request.POST.get('title'),
                'refresh': self.request.POST.get('refresh')
            }

        return {
            'title': 'Widget config',
            'content': self.render_to_string('trionyx/dialog/widget_config.html', {
                'form': form,
                'title': self.request.POST.get('title'),
                'refresh': self.request.POST.get('refresh'),
            }),
            'submit_label': 'Done',
            'config': config
        }

    def handle_dialog(self, code, *args, **kwargs):
        """Handle widget config"""
        return self.display_dialog(code)
