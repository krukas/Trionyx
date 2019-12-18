"""
trionyx.views
~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import csv
import io
import json
import logging
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
from django.core.exceptions import PermissionDenied
from django.http import Http404, StreamingHttpResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib import messages
from watson import search as watson
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from trionyx.views.mixins import ModelClassMixin, SessionValueMixin, ModelPermissionMixin
from trionyx.forms.helper import FormHelper
from trionyx.models import filter_queryset_with_user_filters
from .ajax import JsendView

logger = logging.getLogger(__name__)


# =============================================================================
# List view
# =============================================================================
class ListView(ModelPermissionMixin, TemplateView, ModelClassMixin):
    """List view for showing model"""

    permission_type = 'view'
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

    def get_mass_delete_url(self):
        """Get mass delete url"""
        return reverse('trionyx:model-mass-delete', kwargs=self.kwargs)

    def get_mass_update_url(self):
        """Get mass delete url"""
        return reverse('trionyx:model-mass-update', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        """Add context data to view"""
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.get_title(),
            'content_type_id': ContentType.objects.get_for_model(self.get_model_class()).id,
            'model_config': self.get_model_config(),
            'ajax_url': self.get_ajax_url(),
            'download_url': self.get_download_url(),
            'create_url': self.get_create_url(),
            'header_buttons': self.get_model_config().get_header_buttons(context={
                'page': 'list',
            }),
            'mass_delete_url': self.get_mass_delete_url(),
            'mass_update_url': self.get_mass_update_url(),
            'create_permission': self.get_model_config().has_permission('add', user=self.request.user),
            'change_permission': self.get_model_config().has_permission('change', user=self.request.user),
            'delete_permission': self.get_model_config().has_permission('delete', user=self.request.user),
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
        return self.get_and_save_value('page_size', '10')

    def get_sort(self):
        """Get current sort or sort in session"""
        return self.get_and_save_value('sort', self.get_model_config().list_default_sort)

    def get_search(self):
        """Get current search or search from session, reset page if search is changed"""
        old_search = self.get_session_value('search', '')
        search = self.get_and_save_value('search', '')
        if old_search != search:
            self.page = 1
            self.get_session_value('page', self.page)
        return search

    def get_filters(self):
        """Get all active filters"""
        try:
            return json.loads(self.get_and_save_value('filters', '[]'))
        except json.JSONDecodeError:
            return []

    def get_all_fields(self):
        """Get all available fields"""
        return {
            name: {
                'name': name,
                'label': field['label'],
                'type': field['type'],
                'choices': field['choices'],
            }
            for name, field in self.get_model_config().get_list_fields().items()
        }

    def get_current_fields(self):
        """Get current list to be used"""
        if hasattr(self, 'current_fields') and self.current_fields:
            return self.current_fields

        field_attribute = 'list_{}_{}_fields'.format(self.kwargs.get('app'), self.kwargs.get('model'))
        current_fields = self.request.user.get_attribute(field_attribute, [])
        request_fields = self.request.POST.get('selected_fields', None)

        if request_fields and ','.join(current_fields) != request_fields:
            # TODO validate fields
            current_fields = list(filter(lambda f: f != 'NR', request_fields.split(',')))
            self.request.user.set_attribute(field_attribute, current_fields)
        elif request_fields:
            current_fields = request_fields.split(',')

        if not current_fields:
            config = self.get_model_config()
            current_fields = config.list_default_fields if config.list_default_fields else ['id']

        # TODO check if all fields are still valid, filter out invalid and save
        self.current_fields = current_fields
        return current_fields

    def get_paginator(self):
        """Get paginator"""
        return Paginator(self.get_queryset(), self.get_page_size())

    def get_queryset(self):
        """Get qeuryset for model"""
        query = self.search_queryset()
        query = filter_queryset_with_user_filters(query, self.get_filters(), self.request)

        fields = self.get_all_fields()
        select_related = self.get_model_config().list_select_related if self.get_model_config().list_select_related else []
        for field in self.get_current_fields():
            field_parts = field.split('__')
            if len(field_parts) > 1:
                select_related.append('__'.join(field_parts[:-1]))
            elif fields[field]['type'] == 'related':
                select_related.append(field)

        if select_related:
            query = query.select_related(*set(select_related))

        return query.order_by(self.get_sort())

    def search_queryset(self):
        """Get search query set"""
        queryset = self.get_model_class().objects.get_queryset()
        return watson.filter(queryset, self.get_search(), ranking=False)


class ListJsendView(ModelPermissionMixin, JsendView, ModelListMixin):
    """Ajax list view"""

    permission_type = 'view'

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
            'filters': self.get_filters(),
            'page': page,
            'page_size': self.get_page_size(),
            'num_pages': paginator.num_pages,
            'count': paginator.count,
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
                'url': self.get_model_config().get_absolute_url(item),
                'row_data': [
                    fields[field]['renderer'](item, field)
                    for field in self.get_current_fields()
                ]
            })
        return items


class ListExportView(ModelPermissionMixin, View, ModelListMixin):
    """View for downloading an export of a list view"""

    permission_type = 'view'

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


class ListChoicesJsendView(ModelPermissionMixin, JsendView, ModelListMixin):
    """View for getting choices list for related field"""

    permission_type = 'view'

    def handle_request(self, request, *args, **kwargs):
        """Build choices list for related field"""
        try:
            ModelClass = self.get_model_class()
            fields = request.GET.get('field').split('__')
            RelatedClass = getattr(ModelClass, fields[0]).field.related_model

            for field in fields[1:]:
                RelatedClass = getattr(RelatedClass, field).field.related_model
        except Exception:
            return []
        return list(RelatedClass.objects.values_list('id', 'verbose_name'))


# =============================================================================
# Detail tab views
# =============================================================================
class DetailTabView(ModelPermissionMixin, DetailView, ModelClassMixin):
    """Detail tab view, shows model details in tab view"""

    permission_type = 'view'

    template_name = "trionyx/core/model_view.html"
    """Template name for rendering the view, default is 'trionyx/core/detail_tab_view.html'

        .. note::
            Only overide this if you want to customize the layout of the page.
    """

    model_alias: str = ''
    """Model identifier, default is '<model app name>.<model name>'."""

    title: str = ''
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
            'model_config': self.get_model_config(),
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
            'change_permission': self.get_model_config().has_permission('change', self.object, user=self.request.user),
            'delete_permission': self.get_model_config().has_permission('delete', self.object, user=self.request.user),
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
        from trionyx.views import tabs
        return list(tabs.get_tabs(self.get_model_alias(), self.object))

    def dispatch(self, request, *args, **kwargs):
        """Validate if user can use view"""
        if False:  # TODO do permission check based on Model
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class DetailTabJsendView(ModelPermissionMixin, JsendView, ModelClassMixin):
    """View for getting tab view with ajax"""

    permission_type = 'view'

    def handle_request(self, request, app, model, pk):
        """Render and return tab"""
        from trionyx.views import tabs

        tab_code = request.GET.get('tab')
        model_alias = request.GET.get('model_alias')
        model_alias = model_alias if model_alias else '{}.{}'.format(app, model)

        # TODO permission check

        item = tabs.get_tab(model_alias, self.get_object(), tab_code)

        return {
            'header_buttons': render_to_string('trionyx/base/model_header_buttons.html', {
                'header_buttons': self.get_model_config().get_header_buttons(self.get_object(), {
                    'page': 'view',
                    'model_alias': model_alias,
                    'tab': tab_code,
                }),
            }, request=request),
            'content': item.get_layout(self.get_object()).render(request),
        }

    def get_object(self):
        """Get object"""
        if not hasattr(self, 'object'):
            ModelClass = self.get_model_class()
            self.object = ModelClass.objects.get(id=self.kwargs.get('pk'))
        return self.object


class LayoutView(DetailTabView):
    """Display layout for model"""

    permission_type = 'view'

    template_name = "trionyx/core/layout_view.html"

    def get_context_data(self, **kwargs):
        """Add layout to context"""
        context = super().get_context_data(**kwargs)
        from trionyx.views import layouts
        try:
            context['layout'] = layouts.get_layout(self.kwargs.get('code'), self.object).render(self.request)
        except Exception:
            raise Http404()
        return context


class LayoutUpdateView(JsendView, ModelClassMixin):
    """Update whole or section of an layout"""

    def handle_request(self, request, pk, code, **kwargs):
        """Render layout or given component for layout"""
        from trionyx.views import layouts
        layout = layouts.get_layout(
            code,
            self.get_model_class().objects.get(id=pk),
            request.GET.get('layout_id')
        )

        component_id = request.GET.get('component')
        if component_id:
            comp, _ = layout.find_component_by_id(component_id)
            return comp.render({}, request)
        else:
            return ''.join(comp.render({}, request) for comp in layout.components)


# =============================================================================
# Update/Create/Delete view
# =============================================================================
class UpdateView(ModelPermissionMixin, DjangoUpdateView, ModelClassMixin):
    """Update view that renders view with crispy-forms"""

    permission_type = 'change'

    template_name = 'trionyx/core/model_update.html'

    title: str = ''
    """Title of page, default is: Update <object.__str__>"""

    submit_value: str = ''
    """Value of the form submit button"""

    cancel_url: str = ''
    """Url code for cancel button, when not set object.get_absolute_url is used"""

    @property
    def success_url(self):
        """Return success url"""
        return self.get_model_config().get_absolute_url(self.object)

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
        from trionyx.forms import form_register
        if self.kwargs.get('code'):
            return form_register.get_form(self.get_model_class(), self.kwargs.get('code'))
        return form_register.get_edit_form(self.get_model_class())

    def get_form(self, form_class=None):
        """Get form for model"""
        if not hasattr(self, 'form'):
            self.form = super().get_form(form_class)

        if not getattr(self.form, 'helper', None):
            self.form.helper = FormHelper(self.form)
            self.form.helper.form_tag = False
        else:
            self.form.helper.form_tag = False
        return self.form

    def get_context_data(self, **kwargs):
        """Add context data to view"""
        context = super().get_context_data(**kwargs)

        context.update({
            'title': self.get_form().get_title() if hasattr(self.get_form(), 'get_title') else self.title,
            'submit_value': (self.get_form().get_submit_label()
                             if hasattr(self.get_form(), 'get_submit_label')
                             else self.submit_value),
            'header_buttons': list(
                self.get_model_config().get_header_buttons(self.object, {'page': 'edit'})
            ),
            'cancel_url': self.cancel_url,
            'object_url': self.get_model_config().get_absolute_url(self.object),
        })

        return context

    def form_valid(self, form):
        """Add success message"""
        response = super().form_valid(form)
        messages.success(self.request, _("Successfully saved ({})").format(self.object))
        return response

    def form_invalid(self, form):
        """Form invalid"""
        logger.debug(json.dumps(form.errors))
        return super().form_invalid(form)


class CreateView(ModelPermissionMixin, DjangoCreateView, ModelClassMixin):
    """Create view that renders view with crispy-forms"""

    permission_type = 'add'

    template_name = 'trionyx/core/model_create.html'

    title = None
    """Title of page, default is: Update <object.__str__>"""

    submit_value = None
    """Value of the form submit button"""

    cancel_url = None
    """Url code for cancel button, when not set model list view is used"""

    @property
    def success_url(self):
        """Return success url"""
        return self.get_model_config().get_absolute_url(self.object)

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
        from trionyx.forms import form_register
        if self.kwargs.get('code'):
            return form_register.get_form(self.get_model_class(), self.kwargs.get('code'))
        return form_register.get_create_form(self.get_model_class())

    def get_form(self, form_class=None):
        """Get form for model"""
        if not hasattr(self, 'form'):
            self.form = super().get_form(form_class)

        if not getattr(self.form, 'helper', None):
            self.form.helper = FormHelper(self.form)
            self.form.helper.form_tag = False
        else:
            self.form.helper.form_tag = False
        return self.form

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
            'title': self.get_form().get_title() if hasattr(self.get_form(), 'get_title') else self.title,
            'submit_value': (self.get_form().get_submit_label()
                             if hasattr(self.get_form(), 'get_submit_label')
                             else self.submit_value),
            'cancel_url': self.get_cancel_url(),
            'model_verbose_name': self.get_model_class()._meta.verbose_name,
        })

        return context

    def form_valid(self, form):
        """Add success message"""
        response = super().form_valid(form)
        messages.success(self.request, _("Successfully created ({})").format(self.object))
        return response

    def form_invalid(self, form):
        """Form invalid"""
        logger.debug(json.dumps(form.errors))
        return super().form_invalid(form)


class DeleteView(ModelPermissionMixin, DjangoDeleteView, ModelClassMixin):
    """Delete view"""

    permission_type = 'delete'

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
            'cancel_url': self.cancel_url,
            'object_url': self.get_model_config().get_absolute_url(self.object)
        })
        return context

    def get_success_url(self):
        """Get success url"""
        messages.success(self.request, _("Successfully deleted ({})").format(self.object))
        if self.success_url:
            return reverse(self.success_url)

        if 'app' in self.kwargs and 'model' in self.kwargs:
            return reverse('trionyx:model-list', kwargs={
                'app': self.kwargs.get('app'),
                'model': self.kwargs.get('model'),
            })

        return '/'
