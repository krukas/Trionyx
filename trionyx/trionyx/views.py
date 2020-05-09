"""
trionyx.trionyx.view.accounts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import os
import re
import json
import logging
from collections import OrderedDict

from docutils.core import publish_parts
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import Permission
from django.shortcuts import redirect
from django.urls import reverse
from watson import search as watson
from django.contrib.contenttypes.models import ContentType
from django.views.generic import TemplateView
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.forms.widgets import SelectMultiple

from trionyx.models import get_class
from trionyx.views import UpdateView, DetailTabView, DialogView, JsendView
from trionyx.views.mixins import ModelClassMixin, ModelPermissionMixin
from trionyx.config import models_config
from trionyx.widgets import widgets
from trionyx import utils
from trionyx.forms.helper import FormHelper
from trionyx.forms import form_register, modelform_factory, ModelAjaxChoiceField
from trionyx.models import filter_queryset_with_user_filters
from trionyx.trionyx.tasks import MassUpdateTask

User = get_class('trionyx.User')
Task = get_class('trionyx.Task')

logger = logging.getLogger(__name__)


def basic_auth(request, user_type):
    """View that can be used for basic-auth like Nginx ngx_http_auth_request_module"""
    if user_type == 'superuser' and request.user.is_authenticated and request.user.is_superuser:
        return HttpResponse('OK')
    if user_type == 'user' and request.user.is_authenticated:
        return HttpResponse('OK')
    return HttpResponse('NOK', status=403)


def media_nginx_accel(request, path):
    """
    Location /protected/ {
        internal;
        alias <complete path to project root dir>;
    }

    """
    response = HttpResponse(status=200)
    response['Content-Type'] = ''
    response['X-Accel-Redirect'] = '/protected' + request.path
    return response


class LoginView(DjangoLoginView):
    """Trionyx login view"""

    redirect_authenticated_user = True

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

        parent = ['jstree']

        if model_config.app_label not in added_apps:
            jstree.append({
                'id': '.'.join([*parent, model_config.app_label]),
                'parent': '#',
                'text': model_config.get_app_verbose_name(),
                'state': {
                    'disabled': disabled,
                }
            })
            added_apps.append(model_config.app_label)

        parent.append(model_config.app_label if model_config.app_label != 'auth' else 'trionyx')

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
# Ajax form views
# =============================================================================
def ajaxFormModelChoices(request, id):
    """View for select2 ajax data request"""
    if id not in ModelAjaxChoiceField.registered_fields:
        return JsonResponse({})

    field = ModelAjaxChoiceField.registered_fields[id]
    query = field.queryset.order_by('verbose_name')

    search = request.GET.get('q', None)
    if search:
        config = models_config.get_config(query.model)
        if not config.disable_search_index:
            query = watson.filter(query, search, ranking=False)
        else:
            query = query.filter(verbose_name__contains=search)

    pages = Paginator(query, 20)
    page = pages.page(int(request.GET.get('page', 1)))

    result = [
        {'id': '', 'text': '------'}
    ] if not isinstance(field.widget, SelectMultiple) and not field.required and page.number == 1 else []

    return JsonResponse({
        'results': result + [{
            'id': row[0],
            'text': row[1],
        } for row in page.object_list.values_list('id', 'verbose_name')],
        'pagination': {
            'more': page.has_next(),
        }
    })


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
        try:
            modelClass = ContentType.objects.get_for_id(request.GET.get('id')).model_class()
        except ContentType.DoesNotExist:
            return {}
        config = models_config.get_config(modelClass)

        return {
            'id': request.GET.get('id'),
            'fields': {
                name: {
                    'name': name,
                    'label': str(field['label']),
                    'type': field['type'],
                    'choices': field['choices'],
                    'choices_url': field.get('choices_url', None)
                }
                for name, field in config.get_list_fields().items()
            }
        }


class UserTasksJsend(JsendView):
    """User tasks view"""

    def handle_request(self, request):
        """Get user open tasks"""
        tasks = []

        tasks.extend([
            task for task in Task.objects.filter(user=request.user, status=Task.SCHEDULED).order_by('-scheduled_at')
        ])

        tasks.extend([
            task for task in Task.objects.filter(
                user=request.user,
                status__in=[Task.QUEUE, Task.LOCKED, Task.RUNNING]
            ).order_by('-started_at')
        ])

        if len(tasks) < 10:
            tasks.extend([
                task for task in Task.objects.filter(
                    user=request.user, status__in=[Task.COMPLETED, Task.FAILED]
                ).order_by('-started_at')[: 10 - len(tasks)]
            ])

        return [
            {
                'id': task.id,
                'status': task.status,
                'status_display': task.get_status_display(),
                'description': task.description,
                'progress': task.progress,
                'url': task.get_absolute_url(),
            } for task in tasks
        ]


# =============================================================================
# Changelog
# =============================================================================
class ChangelogDialog(DialogView):
    """Dialog to show app changelog based on CHANGELOG.rst"""

    def display_dialog(self):
        """Display changelog"""
        changelog_path = os.path.join(settings.BASE_DIR, 'CHANGELOG.rst')

        if os.path.isfile(changelog_path):
            with open(changelog_path, 'r', encoding='utf-8') as _file:
                content = publish_parts(_file.read(), writer_name='html')['html_body']
        else:
            content = ''

        if settings.TX_CHANGELOG_HASHTAG_URL:
            link_re = r'<a href="{link}" target="_blank">#\1</a>'.format(link=settings.TX_CHANGELOG_HASHTAG_URL.format(tag='\\1'))
            content = re.sub(r"#([\d\w\-]+)", link_re, content)

        return {
            'title': str(_('Changelog for {name}')).format(name=settings.TX_APP_NAME),
            'content': f'<div class="changelog-wrapper">{content}</div>',
            'submit_label': _("Don't show again") if self.request.GET.get('show') else False,
        }

    def handle_dialog(self):
        """Save shown changelog version"""
        self.request.user.set_attribute('trionyx_last_shown_version', utils.get_app_version())
        return {
            'close': True,
        }


# =============================================================================
# Sidebar
# =============================================================================
class SidebarJsend(JsendView):
    """Model sidebar view"""

    def handle_request(self, request, app, model, pk, code):
        """Return given sidebar"""
        from trionyx.views import sidebars
        config = models_config.get_config(f'{app}.{model}')
        obj = config.model.objects.get(id=pk)
        return sidebars.get_sidebar(config.model, code)(request, obj)


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

    def display_dialog(self):
        """Handle widget config"""
        code = self.kwargs.get('code')
        if code not in widgets:
            return {
                'title': _('Widget does not exists')
            }

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
            elif '__post__' in self.request.POST:
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

    def handle_dialog(self):
        """Handle widget config"""
        return self.display_dialog()


# Mass actions
class MassDeleteDialog(DialogView):
    """Mass delete dialog"""

    permission_type = 'delete'

    def has_permission(self, request):
        """Check permission"""
        config = self.get_model_config()

        if config.disable_delete:
            return False

        return request.user.has_perm('{app_label}.{type}_{model_name}'.format(
            app_label=config.app_label,
            type=self.permission_type,
            model_name=config.model_name,
        ).lower())

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


class MassUpdateView(ModelPermissionMixin, TemplateView, ModelClassMixin):
    """Mass update view"""

    template_name = 'trionyx/core/model_mass_update.html'
    permission_type = 'change'

    def get(self, *args, **kwargs):
        """Render mass update form"""
        context = self.get_context_data(**kwargs)
        all = self.request.GET.get('all', '0')
        ids = self.request.GET.get('ids', '')
        filters = self.request.GET.get('filters', '[]')
        query = self.get_queryset(all, ids, filters)

        if not query:
            messages.error(self.request, _('You must make a selection'))
            return HttpResponseRedirect(reverse('trionyx:model-list', kwargs=self.kwargs))

        context.update({
            'model_name': self.get_model_config().get_verbose_name(),
            'model_name_plural': self.get_model_config().get_verbose_name_plural(),
            'cancel_url': reverse('trionyx:model-list', kwargs=self.kwargs),
            'all': all,
            'ids': ids,
            'filters': filters,
            'count': query.count(),
            'form': self.get_form(),
            'checked_fields': [],
        })
        return self.render_to_response(context)

    def post(self, *args, **kwargs):
        """Handle mass update form"""
        all = self.request.POST.get('trionyx_all', '0')
        ids = self.request.POST.get('trionyx_ids', '')
        filters = self.request.POST.get('trionyx_filters', '[]')
        query = self.get_queryset(all, ids, filters)

        if not query:
            messages.error(self.request, _('You must make a selection'))
            return HttpResponseRedirect(reverse('trionyx:model-list', kwargs=self.kwargs))

        form = self.get_form(self.request.POST)

        if not form.is_valid():
            print(form.errors)
            context = self.get_context_data(**kwargs)
            context.update({
                'model_name': self.get_model_config().get_verbose_name(),
                'model_name_plural': self.get_model_config().get_verbose_name_plural(),
                'cancel_url': reverse('trionyx:model-list', kwargs=self.kwargs),
                'all': all,
                'ids': ids,
                'filters': filters,
                'count': query.count(),
                'form': form,
                'checked_fields': form.checked_fields,
            })
            return self.render_to_response(context)

        # Get data from form
        data = {}
        for field in form.fields:
            if self.request.POST.get('change_{}'.format(field), False):
                data[field] = form.cleaned_data[field]

        # Start update task
        MassUpdateTask().delay(
            all=all,
            ids=ids,
            filters=filters,
            data=data,

            task_description=_('Mass update {count} {model_name}').format(
                count=query.count(),
                model_name=self.get_model_config().get_verbose_name_plural(),
            ),
            task_model=self.get_model_class(),
        )

        # Add message
        messages.success(self.request, _('Successfully started task for updating {count} {model_name}').format(
            count=query.count(),
            model_name=self.get_model_config().get_verbose_name_plural(),
        ))

        # return to list view
        return HttpResponseRedirect(reverse('trionyx:model-list', kwargs=self.kwargs))

    def get_queryset(self, all, ids, filters):
        """Get queryset"""
        query = self.get_model_class().objects.get_queryset()

        if all == '1':
            return filter_queryset_with_user_filters(query, json.loads(filters))
        else:
            return query.filter(id__in=[int(id) for id in filter(None, ids.split(','))])

    def get_form(self, data=None):
        """Get form class"""
        model_config = self.get_model_config()
        fields = []

        model_fields = [f.name for f in model_config.get_fields()]
        forms = form_register.get_all_forms(self.get_model_class())
        if forms:  # Only use fields that ara also in forms
            for Form in forms:
                fields.extend([name for name in Form.base_fields if name in model_fields])
                fields.extend([name for name in Form.declared_fields if name in model_fields])
        else:
            fields = [f.name for f in model_config.get_fields()]

        FormClass = modelform_factory(self.get_model_class(), fields=sorted(list(set(fields))))
        FormClass._post_clean = lambda self: None
        form = FormClass(data)

        # Disable fields that are not checked for change
        form.checked_fields = []
        for field in form.fields:
            form.fields[field].required = False
            if not (data and data.get('change_{}'.format(field), False)):
                form.fields[field].widget.attrs['readonly'] = True
                form.fields[field].widget.attrs['disabled'] = True
            else:
                form.checked_fields.append(field)

        return form
