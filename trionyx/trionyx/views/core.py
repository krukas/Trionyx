"""
trionyx.trionyx.views.core
~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import csv
import io
from collections import OrderedDict

from django.apps import apps
from django.views.generic import (
    View,
    TemplateView,
    DetailView,
    UpdateView as
    DjangoUpdateView,
    CreateView as DjangoCreateView,
    DeleteView as DjangoDeleteView
)
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import PermissionDenied
from django.http import Http404, StreamingHttpResponse
from django_jsend import JsendView
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib import messages  # noqa F401 TODO add success message to create/edit/delete
from django.template.loader import render_to_string

from watson import search as watson
from crispy_forms.helper import FormHelper

from trionyx.navigation import tabs
from trionyx.config import models_config


def media_nginx_accel(request, path):
    """
    location /protected/ {
        internal;
        root <complete path to project root dir>;
    }

    """
    response = HttpResponse(status=200)
    response['Content-Type'] = ''
    response['X-Accel-Redirect'] = '/protected' + request.path
    return response


class ModelClassMixin:
    """Mixen for getting model class"""

    def get_model_class(self):
        """Get model class"""
        if getattr(self, 'model', None):
            return self.model
        elif getattr(self, 'object', None):
            return self.object.__class__
        elif 'app' in self.kwargs and 'model' in self.kwargs:
            return apps.get_model(self.kwargs.get('app'), self.kwargs.get('model'))
        elif hasattr(self, 'get_queryset'):
            return self.get_queryset().model
        else:
            return None

    def get_model_config(self):
        """Get Trionyx model config"""
        if not hasattr(self, '__config'):
            setattr(self, '__config', models_config.get_config(self.get_model_class()))
        return getattr(self, '__config', None)


class ModelPermission:
    """Check Model permission"""

    def dispatch(self, request, *args, **kwargs):
        """Validate if user can use view"""
        if False:  # TODO do permission check based on Model
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class SessionValueMixin:
    """Mixin for handling session values"""

    def get_and_save_value(self, name, default=None):
        """Get value from request/session and save value to session"""
        if getattr(self, name, None):
            return getattr(self, name)

        value = self.get_session_value(name, default)
        value = self.request.POST.get(name, value)
        self.save_value(name, value)
        return value

    def get_session_value(self, name, default=None):
        """Get value from session"""
        session_name = 'list_{}_{}_{}'.format(self.kwargs.get('app'), self.kwargs.get('model'), name)
        return self.request.session.get(session_name, default)

    def save_value(self, name, value):
        """Save value to session"""
        session_name = 'list_{}_{}_{}'.format(self.kwargs.get('app'), self.kwargs.get('model'), name)
        self.request.session[session_name] = value
        setattr(self, name, value)
        return value


# =============================================================================
# List view
# =============================================================================
class ListView(TemplateView, ModelClassMixin):
    """List view for showing model"""

    template_name = "trionyx/core/model_list.html"

    model = None
    """Model class default will try get model based on url kwargs app, model"""

    title = None
    """Title of page default is model verbose_name_plural"""

    ajax_url = None
    """Ajax url used to get model list data"""

    download_url = None
    """Download url used to get model list data"""

    def get_title(self):
        """Get page title"""
        if self.title:
            return self.title
        return self.get_model_class()._meta.verbose_name_plural

    def get_ajax_url(self):
        """Get ajax url"""
        if self.ajax_url:
            return self.ajax_url
        return reverse('trionyx:model-list-ajax', kwargs=self.kwargs)

    def get_download_url(self):
        """Get ajax url"""
        if self.download_url:
            return self.download_url
        return reverse('trionyx:model-list-download', kwargs=self.kwargs)

    def get_create_url(self):
        """Get create url"""
        return reverse('trionyx:model-create', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        """Add context data to view"""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.get_title(),
            'ajax_url': self.get_ajax_url(),
            'download_url': self.get_download_url(),
            'create_url': self.get_create_url(),
        })
        return context


class ModelListMixin(ModelClassMixin, SessionValueMixin):
    """Mixin for handling model list"""

    def get_page(self, paginator):
        """Get current page or page in session"""
        page = int(self.get_and_save_value('page', 1))
        if page < 1:
            return self.save_value('page', 1)

        if page > paginator.num_pages:
            return self.save_value('page', paginator.num_pages)
        return page

    def get_page_size(self):
        """Get current page size or page size in session"""
        return self.get_and_save_value('page_size', 10)

    def get_sort(self):
        """Get current sort or sort in session"""
        return self.get_and_save_value('sort', '-id')

    def get_search(self):
        """Get current search or search from session, reset page if search is changed"""
        old_search = self.get_session_value('search', '')
        search = self.get_and_save_value('search', '')
        if old_search != search:
            self.page = 1
            self.get_session_value('page', self.page)
        return search

    def get_all_fields(self):
        """Get all aviable fields"""
        return {
            name: {
                'name': name,
                'label': field['label'],
            }
            for name, field in self.get_model_config().get_list_fields().items()
        }

    def get_current_fields(self):
        """Get current list to be used"""
        if hasattr(self, 'current_fields') and self.current_fields:
            return self.current_fields

        field_attribute = 'list_{}_{}_fields'.format(self.kwargs.get('app'), self.kwargs.get('model'))
        current_fields = self.request.user.attributes.get_attribute(field_attribute, [])
        request_fields = self.request.POST.get('selected_fields', None)

        if request_fields and ','.join(current_fields) != request_fields:
            # TODO validate fields
            current_fields = request_fields.split(',')
            self.request.user.attributes.set_attribute(field_attribute, current_fields)
        elif request_fields:
            current_fields = request_fields.split(',')

        if not current_fields:
            config = self.get_model_config()
            current_fields = config.list_default_fields if config.list_default_fields else ['created_at', 'id']

        self.current_fields = current_fields
        return current_fields

    def get_paginator(self):
        """Get paginator"""
        return Paginator(self.get_queryset(), self.get_page_size())

    def get_queryset(self):
        """Get qeuryset for model"""
        query = self.search_queryset()
        # TODO Apply filters
        return query.order_by(self.get_sort())

    def search_queryset(self):
        """Get search query set"""
        queryset = self.get_model_class().objects.get_queryset()

        if self.get_model_config().list_select_related:
            queryset = queryset.select_related(*self.get_model_config().list_select_related)

        return watson.filter(queryset, self.get_search(), ranking=False)


class ListJsendView(JsendView, ModelListMixin):
    """Ajax list view"""

    def __init__(self, *args, **kwargs):
        """Init ListJsendView"""
        super().__init__(*args, **kwargs)
        self.page = None
        self.page_size = None
        self.sort = None
        self.fields = None

    def handle_request(self, request, *args, **kwargs):
        """Give back list items + config"""
        paginator = self.get_paginator()
        # Call search first, it will reset page if search is changed
        search = self.get_search()
        page = self.get_page(paginator)
        items = self.get_items(paginator, page)
        return {
            'search': search,
            'page': page,
            'page_size': self.get_page_size(),
            'num_pages': paginator.num_pages,
            'sort': self.get_sort(),
            'current_fields': self.get_current_fields(),
            'fields': self.get_all_fields(),

            'items': items,
        }

    def get_items(self, paginator, current_page):
        """Get list items for current page"""
        fields = self.get_model_config().get_list_fields()

        page = paginator.page(current_page)

        items = []
        for item in page:
            items.append({
                'id': item.id,
                'url': item.get_absolute_url(),
                'row_data': [
                    fields[field]['renderer'](item, field)
                    for field in self.get_current_fields()
                ]
            })
        return items


class ListExportView(View, ModelListMixin):
    """View for downloading an export of a list view"""

    def post(self, request, app, model, **kwargs):
        """Handle post request"""
        return self.csv_response()

    def items(self):
        """Get all list items"""
        query = self.get_queryset()
        fields = self.get_model_config().get_list_fields()

        for item in query.iterator():
            row = OrderedDict()
            for field_name in self.get_current_fields():
                field = fields.get(field_name)
                if not field_name:
                    row[field_name] = ''

                if hasattr(item, field['field']):
                    row[field_name] = getattr(item, field['field'])
                else:
                    row[field_name] = ''  # TODO Maybe render field ans strip html?
            yield row

    def csv_response(self):
        """Get csv response"""
        def stream():
            """Create data stream generator"""
            stream_file = io.StringIO()
            csvwriter = csv.writer(stream_file, delimiter=',', quotechar='"')

            csvwriter.writerow(self.get_current_fields())

            for index, item in enumerate(self.items()):
                csvwriter.writerow([value for index, value in item.items()])
                stream_file.seek(0)
                data = stream_file.read()
                stream_file.seek(0)
                stream_file.truncate()
                yield data

        response = StreamingHttpResponse(stream(), content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename={}.csv".format(self.get_model_config().model_name.lower())
        return response


# =============================================================================
# Detail tab views
# =============================================================================
class DetailTabView(DetailView, ModelClassMixin):
    """Detail tab view, shows model details in tab view"""

    template_name = "trionyx/core/model_view.html"
    """Template name for rendering the view, default is 'trionyx/core/detail_tab_view.html'

        .. note::
            Only overide this if you want to customize the layout of the page.
    """

    model_alias = None
    """Model identifier, default is '<model app name>.<model name>'."""

    title = None
    """Page title if not set object __str__ is used"""

    def get_queryset(self):
        """Get queryset based on url params(<app>, <mode>) if model is not set on class"""
        if self.queryset is None and not self.model:
            try:
                ModelClass = apps.get_model(self.kwargs.get('app'), self.kwargs.get('model'))
                return ModelClass._default_manager.all()
            except LookupError:
                raise Http404()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        """Add context data to view"""
        context = super().get_context_data(**kwargs)
        tabs = self.get_active_tabs()
        context.update({
            'page_detail_tabs': tabs,
            'active_tab': tabs[0].code if tabs else '',
            'app_label': self.get_app_label(),
            'model_name': self.get_model_name(),
            'model_alias': self.get_model_alias(),
            'model_verbose_name': self.object._meta.verbose_name.title(),
            'back_url': self.get_back_url(),
            'edit_url': self.get_edit_url(),
            'delete_url': self.get_delete_url(),
            'title': self.title,
        })
        return context

    def get_back_url(self):
        """Get back url"""
        return reverse('trionyx:model-list', kwargs={
            'app': self.get_app_label(),
            'model': self.get_model_name(),
        })

    def get_delete_url(self):
        """Get model object delete url"""
        return reverse('trionyx:model-delete', kwargs={
            'app': self.get_app_label(),
            'model': self.get_model_name(),
            'pk': self.object.id
        })

    def get_edit_url(self):
        """Get model object edit url"""
        return reverse('trionyx:model-edit', kwargs={
            'app': self.get_app_label(),
            'model': self.get_model_name(),
            'pk': self.object.id
        })

    def get_model_alias(self):
        """Get model alias"""
        if self.model_alias:
            return self.model_alias
        return '{}.{}'.format(self.get_app_label(), self.get_model_name())

    def get_app_label(self):
        """Get model app label"""
        return self.object._meta.app_label

    def get_model_name(self):
        """Get model name"""
        return self.object._meta.model_name

    def get_active_tabs(self):
        """Get all active tabs"""
        return list(tabs.get_tabs(self.get_model_alias(), self.object))

    def dispatch(self, request, *args, **kwargs):
        """Validate if user can use view"""
        if False:  # TODO do permission check based on Model
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class DetailTabJsendView(JsendView, ModelClassMixin):
    """View for getting tab view with ajax"""

    def handle_request(self, request, app, model, pk):
        """Render and return tab"""
        ModelClass = self.get_model_class()
        object = ModelClass.objects.get(id=pk)

        tab_code = request.GET.get('tab')
        model_alias = request.GET.get('model_alias')
        model_alias = model_alias if model_alias else '{}.{}'.format(app, model)

        # TODO permission check

        item = tabs.get_tab(model_alias, object, tab_code)

        return item.get_layout(object).render(request)


# =============================================================================
# Update/Create/Delete view
# =============================================================================
class UpdateView(DjangoUpdateView, ModelClassMixin):
    """Update view that renders view with crispy-forms"""

    template_name = 'trionyx/core/model_update.html'

    title = None
    """Title of page, default is: Update <object.__str__>"""

    submit_value = None
    """Value of the form submit button"""

    cancel_url = None
    """Url code for cancel button, when not set object.get_absolute_url is used"""

    def get_queryset(self):
        """Get queryset based on url params(<app>, <mode>) if model is not set on class"""
        if self.queryset is None and not self.model:
            try:
                return self.get_model_class()._default_manager.all()
            except LookupError:
                raise Http404()
        return super().get_queryset()

    def get_form_class(self):
        """Get form class for model"""
        if self.form_class:
            return self.form_class
        return self.get_model_config().get_edit_form()

    def get_form(self, form_class=None):
        """Get form for model"""
        form = super().get_form(form_class)

        if not getattr(form, 'helper', None):
            form.helper = FormHelper()
            form.helper.form_tag = False
        else:
            form.helper.form_tag = False
        return form

    def get_context_data(self, **kwargs):
        """Add context data to view"""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            'submit_value': self.submit_value,
            'cancel_url': self.cancel_url,
        })

        return context

    def form_valid(self, form):
        """Add success message"""
        response = super().form_valid(form)
        messages.success(self.request, "Successfully saved ({})".format(self.object))
        return response


class CreateView(DjangoCreateView, ModelClassMixin):
    """Create view that renders view with crispy-forms"""

    template_name = 'trionyx/core/model_create.html'

    title = None
    """Title of page, default is: Update <object.__str__>"""

    submit_value = None
    """Value of the form submit button"""

    cancel_url = None
    """Url code for cancel button, when not set model list view is used"""

    def get_queryset(self):
        """Get queryset based on url params(<app>, <mode>) if model is not set on class"""
        if self.queryset is None and not self.model:
            try:
                return self.get_model_class()._default_manager.all()
            except LookupError:
                raise Http404()
        return super().get_queryset()

    def get_form_class(self):
        """Get form class for model"""
        if self.form_class:
            return self.form_class
        return self.get_model_config().get_create_form()

    def get_form(self, form_class=None):
        """Get form for model"""
        form = super().get_form(form_class)

        if not getattr(form, 'helper', None):
            form.helper = FormHelper()
            form.helper.form_tag = False
        else:
            form.helper.form_tag = False
        return form

    def get_cancel_url(self):
        """Get cancel url"""
        if self.cancel_url:
            return self.cancel_url

        ModelClass = self.get_model_class()
        return reverse('trionyx:model-list', kwargs={
            'app': ModelClass._meta.app_label,
            'model': ModelClass._meta.model_name,
        })

    def get_context_data(self, **kwargs):
        """Add context data to view"""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            'submit_value': self.submit_value,
            'cancel_url': self.get_cancel_url(),
            'model_verbose_name': self.get_model_class()._meta.verbose_name
        })

        return context

    def form_valid(self, form):
        """Add success message"""
        response = super().form_valid(form)
        messages.success(self.request, "Successfully created ({})".format(self.object))
        return response


class DeleteView(DjangoDeleteView, ModelClassMixin):
    """Delete view"""

    template_name = 'trionyx/core/model_delete.html'

    title = None
    """Title of page, default is: Update <object.__str__>"""

    submit_value = None
    """Value of the form submit button"""

    cancel_url = None
    """Url code for cancel button, when not set model list view is used"""

    def get_queryset(self):
        """Get queryset based on url params(<app>, <mode>) if model is not set on class"""
        if self.queryset is None and not self.model:
            try:
                return self.get_model_class()._default_manager.all()
            except LookupError:
                raise Http404()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        """Add context data to view"""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            'submit_value': self.submit_value,
            'cancel_url': self.cancel_url
        })
        return context

    def get_success_url(self):
        """Get success url"""
        messages.success(self.request, "Successfully deleted ({})".format(self.object))
        if self.success_url:
            return reverse(self.success_url)

        if 'app' in self.kwargs and 'model' in self.kwargs:
            return reverse('trionyx:model-list', kwargs={
                'app': self.kwargs.get('app'),
                'model': self.kwargs.get('model'),
            })

        return '/'


# =============================================================================
# Dialog views
# =============================================================================
class DialogView(View, ModelClassMixin):
    """
    Dialog view used for showing dialog popup with ajax.

    **Example**

    .. code-block:: python

        # apps/your_app/views.py

        class HelloWorldDialogView(DialogView):

            def display_dialog(self):
                return {
                    "title": "Hello world",
                    "content": self.render_to_string('your_app/dialog/hello_world.html'),
                }

    **Calling in frontend**

    .. code-block:: django

        <button class="btn btn-primary btn-block"
            onClick="openDialog('{% url 'hello:world' %}', {/* dialog options */})">
            Hello World
        </button>
    """

    permission = None
    """Permission of dialog, when not set and model is set model view permission is used"""

    model_permission = 'read'
    """When no permission is set will use this for model permission"""

    model = None
    """
    Model that will be auto loaded, when set the url mus contain a `pk` parameter.
    Model can also be set with the url with the `app` and `model` parameter.

    Loaded model object is available as self.object and self.<object name lowercase>
    """

    def get(self, request, *args, **kwargs):
        """Handle get request"""
        try:
            kwargs = self.load_object(kwargs)
        except Exception as e:
            return self.render_te_response({
                'title': str(e),
            })

        if not self.has_permission(request):
            return self.render_te_response({
                'title': 'No access',
            })
        return self.render_te_response(self.display_dialog(*args, **kwargs))

    def post(self, request, *args, **kwargs):
        """Handle post request"""
        try:
            kwargs = self.load_object(kwargs)
        except Exception as e:
            return self.render_te_response({
                'title': str(e),
            })

        if not self.has_permission(request):
            return self.render_te_response({
                'title': 'No access',
            })
        return self.render_te_response(self.handle_dialog(*args, **kwargs))

    def load_object(self, kwargs):
        """Load object and model config and remove pk from kwargs"""
        self.object = None
        self.config = None
        self.model = self.get_model_class()
        kwargs.pop('app', None)
        kwargs.pop('model', None)

        if self.model and kwargs.get('pk', False):
            try:
                self.object = self.model.objects.get(pk=kwargs.pop('pk'))
            except Exception:
                raise Exception("Could not load {}".format(self.model.__name__.lower()))
            setattr(self, self.model.__name__.lower(), self.object)

        return kwargs

    def has_permission(self, request):
        """Check if user has permission"""
        if not self.object and not self.permission:
            return True

        if not self.permission:
            return request.user.has_perm('{}_{}'.format(
                self.model_permission,
                self.object.__class__.__name__.lower()), self.object
            )

        return request.user.has_perm(self.permission)

    def render_to_string(self, template_file, context):
        """Render given template to string and add object to context"""
        context = context if context else {}
        if self.object:
            context['object'] = self.object
            context[self.object.__class__.__name__.lower()] = self.object
        return render_to_string(template_file, context, self.request)

    def display_dialog(self, *args, **kwargs):
        """
        Override this function to display a dialog popup. Url params are given as function params.

        The function must return a dict that can contain the following data:

        - **title**: Title of the dialog
        - **content**: Html content to display in dialog, shortcut function :class:`trionyx.trionyx.views.core.DialogView.render_to_string`
        - **url (optional)**: Post url for dialog form, must be a link to a DialogView.
        - **submit_label (optional)**: Label of the submit button, when empty submit button is not shown.
        - **redirect_url (optional)**: Redirect page to given url.
        - **close (optional)**: Close dialog.
        """
        return {}

    def handle_dialog(self, *args, **kwargs):
        """
        Override this function to handle and display popup. Url params are given as function params.
        This function must return the same dict structure as :class:`trionyx.trionyx.views.core.DialogView.display_dialog`

        Post data can be retrieved with *self.request.POST*
        """
        return {}

    def render_te_response(self, data):
        """Render data to JsonResponse"""
        if 'submit_label' in data and 'url' not in data:
            data['url'] = self.request.get_full_path()

        return JsonResponse(data)


class UpdateDialog(DialogView):
    """Update dialog view for updating a model"""

    template = 'trionyx/dialog/model_form.html'
    """Template for dialog content"""

    title = "Update {model_name}: {object}"
    """Dialog title model_name and object, variable are given"""

    submit_label = 'save'
    """Dialog submit label value"""

    success_message = '{model_name} ({object}) is successfully updated'
    """Success message on successfully form saved"""

    def get_form_class(self):
        """Get form class for dialog, default will get form from model config"""
        # TODO get form from url param
        return self.get_model_config().get_edit_form()

    def display_dialog(self, *args, **kwargs):
        """Display form and success message when set"""
        form = kwargs.pop('form_instance', None)
        success_message = kwargs.pop('success_message', None)

        if not form:
            form = self.get_form_class()(initial=kwargs, instance=self.object)

        if not hasattr(form, "helper"):
            form.helper = FormHelper()
        form.helper.form_tag = False

        return {
            'title': self.title.format(
                model_name=self.get_model_config().model_name,
                object=str(self.object) if self.object else '',
            ),
            'content': self.render_to_string(self.template, {
                'form': form,
                'success_message': success_message,
            }),
            'submit_label': self.submit_label,
            'success': bool(success_message),
        }

    def handle_dialog(self, *args, **kwargs):
        """Handle form and save and set success message on valid form"""
        form = self.get_form_class()(self.request.POST, initial=kwargs, instance=self.object)

        success_message = None
        if form.is_valid():
            obj = form.save()
            success_message = self.success_message.format(
                model_name=self.get_model_config().model_name.capitalize(),
                object=str(obj),
            )
        return self.display_dialog(*args, form_instance=form, success_message=success_message, **kwargs)


class CreateDialog(UpdateDialog):
    """Dialog view for creating a model"""

    title = "Create {model_name}"
    submit_label = 'create'
    success_message = '{model_name} ({object}) is successfully created'

    def get_form_class(self):
        """Get create form class"""
        # TODO get form from url param
        return self.get_model_config().get_create_form()
