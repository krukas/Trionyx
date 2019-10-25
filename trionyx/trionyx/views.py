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
from django.contrib.auth.models import Permission
from django.shortcuts import redirect
from django.urls import reverse
from django_jsend import JsendView
from watson import search as watson
from django.contrib.contenttypes.models import ContentType
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.translation import ugettext_lazy as _

from trionyx.views import UpdateView, DetailTabView, DialogView
from trionyx.trionyx.models import User
from trionyx.config import models_config
from trionyx.widgets import widgets
from trionyx import utils
from trionyx.forms.helper import FormHelper
from trionyx.models import filter_queryset_with_user_filters

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


def create_permission_jstree(selected=None, disabled=False):
    """Create permission jstree"""
    selected = selected if selected else []
    jstree = []

    added_apps = ['auth']
    added_models = []
    for permission in Permission.objects.select_related('content_type').all():
        if not permission.content_type.model_class():
            continue

        model_config = models_config.get_config(permission.content_type.model_class())

        if model_config.hide_permissions:
            continue

        if model_config.disable_add and permission.codename == 'add_{}'.format(model_config.model_name):
            continue

        if model_config.disable_change and permission.codename == 'change_{}'.format(model_config.model_name):
            continue

        if model_config.disable_delete and permission.codename == 'delete_{}'.format(model_config.model_name):
            continue

        if model_config.app_label not in added_apps:
            jstree.append({
                'id': model_config.app_label,
                'parent': '#',
                'text': model_config.get_app_verbose_name(),
                'state': {
                    'disabled': disabled,
                }
            })
            added_apps.append(model_config.app_label)

        parent = [model_config.app_label if model_config.app_label != 'auth' else 'trionyx']

        if model_config.model_name not in added_models:
            jstree.append({
                'id': '.'.join([*parent, model_config.model_name]),
                'parent': '.'.join(parent),
                'text': model_config.get_verbose_name_plural(),
                'state': {
                    'disabled': disabled,
                }
            })
            added_models.append(model_config.model_name)

        parent.append(model_config.model_name)
        name = {
            'view_{}'.format(model_config.model_name): _('View'),
            'add_{}'.format(model_config.model_name): _('Add'),
            'change_{}'.format(model_config.model_name): _('Change'),
            'delete_{}'.format(model_config.model_name): _('Delete'),
        }.get(permission.codename, permission.name)

        jstree.append({
            'id': '.'.join([*parent, permission.codename]),
            'parent': '.'.join(parent),
            'text': str(name),
            'state': {
                'selected': permission in selected,
                'disabled': disabled,
            },
            'permission_id': permission.id,
        })

    return jstree


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
            for widget in (
                settings.TX_DEFAULT_DASHBOARD()
                if callable(settings.TX_DEFAULT_DASHBOARD)
                else settings.TX_DEFAULT_DASHBOARD
            ):
                widget = widget.copy()
                widget['i'] = utils.random_string(16)
                dashboard.append(widget)

            self.request.user.set_attribute('tx_dashboard', dashboard)

        context.update({
            'widget_templates': [widget().template for index, widget in widgets.items()],
            'widgets': [{
                'code': widget.code,
                'name': str(widget.name),
                'description': str(widget.description),
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
            'title': _('Widget config'),
            'content': self.render_to_string('trionyx/dialog/widget_config.html', {
                'form': form,
                'title': self.request.POST.get('title'),
                'refresh': self.request.POST.get('refresh'),
            }),
            'submit_label': _('Save'),
            'config': config
        }

    def handle_dialog(self, code, *args, **kwargs):
        """Handle widget config"""
        return self.display_dialog(code)


# Mass actions
class MassDeleteDialog(DialogView):
    """Mass delete dialog"""

    def display_dialog(self, *args, **kwargs):
        """Handle mass delete"""
        query = self.get_model_class().objects.get_queryset()

        if self.request.POST.get('all', '0') == '1':
            query = filter_queryset_with_user_filters(query, json.loads(self.request.POST.get('filters', '[]')))
        else:
            query = query.filter(id__in=[int(id) for id in filter(None, self.request.POST.get('ids', '').split(','))])

        count = query.count()
        if '__post__' in self.request.POST:
            try:
                query.delete()
            except Exception:
                return {
                    'title': _('Something went wrong on deleting the items'),
                }
            return {
                'deleted': True,
            }
        else:
            return {
                'title': _('Deleting {count} {model_name} items').format(
                    count=count,
                    model_name=self.get_model_config().get_verbose_name(False)
                ),
                'content': self.render_to_string('trionyx/dialog/mass_delete.html', {
                    'count': count,
                    'model_name': self.get_model_config().get_verbose_name(False),
                    'all': self.request.POST.get('all', '0'),
                    'filters': self.request.POST.get('filters', '[]'),
                    'ids': self.request.POST.get('ids', ''),
                }),
                'submit_label': _('Delete') if count else None,
            }

    def handle_dialog(self, *args, **kwargs):
        """Handle mass delete"""
        return self.display_dialog()
