from django.apps import apps
from django.views.generic import (
    TemplateView,
    DetailView,
    UpdateView as
    DjangoUpdateView,
    CreateView as DjangoCreateView,
    DeleteView as DjangoDeleteView
)
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django_jsend import JsendView
from django.urls import reverse
from django.core.paginator import Paginator
from functools import reduce
from django.db.models import Q
import operator
from django.contrib import messages  # noqa F401 TODO add success message to create/edit/delete

from crispy_forms.helper import FormHelper

from trionyx.navigation import Tab
from trionyx.config import models_config


class SingleUrlObjectMixin:

    def get_model_class(self):
        if getattr(self, 'model', None):
            return self.model
        elif getattr(self, 'object', None):
            return self.object.__class__
        else:
            return self.get_queryset().model


class ListView(TemplateView):
    template_name = "trionyx/core/model_list.html"

    model = None
    title = None
    ajax_url = None

    def get_model_class(self):
        if not self.model:
            self.model = apps.get_model(self.kwargs.get('app'), self.kwargs.get('model'))
        return self.model

    def get_title(self):
        if self.title:
            return self.title
        return self.get_model_class()._meta.verbose_name_plural

    def get_ajax_url(self):
        if self.ajax_url:
            return self.ajax_url
        return reverse('trionyx:model-list-ajax', kwargs=self.kwargs)

    def get_create_url(self):
        return reverse('trionyx:model-create', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.get_title(),
            'ajax_url': self.get_ajax_url(),
            'create_url': self.get_create_url(),
        })
        return context


class ListJsendView(JsendView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page = None
        self.page_size = None
        self.sort = None
        self.current_fields = None
        self.fields = None

    def handle_request(self, request, app, model):
        model = apps.get_model(app, model)
        paginator = self.get_paginator(model)
        # Call search first, it will reset page if search is changed
        search = self.get_search()
        page = self.get_page(paginator)
        items = self.get_items(model, paginator, page)
        return {
            'search': search,
            'page': page,
            'page_size': self.get_page_size(),
            'num_pages': paginator.num_pages,
            'sort': self.get_sort(),
            'current_fields': self.get_current_fields(),
            'fields': self.get_all_fields(model),

            'items': items,
        }

    def get_page(self, paginator):
        page = int(self.get_and_save_value('page', 1))
        if page < 1:
            return self.save_value('page', 1)

        if page > paginator.num_pages:
            return self.save_value('page', paginator.num_pages)
        return page

    def get_page_size(self):
        return self.get_and_save_value('page_size', 10)

    def get_sort(self):
        return self.get_and_save_value('sort', '-id')

    def get_search(self):
        old_search = self.get_session_value('search', '')
        search = self.get_and_save_value('search', '')
        if old_search != search:
            self.page = 1
            self.get_session_value('page', self.page)
        return search

    def get_all_fields(self, model):
        config = models_config.get_config(model)
        return {
            name: {
                'label': field['label'],
            }
            for name, field in config.get_list_fields().items()
        }

    def get_current_fields(self):
        if self.current_fields:
            return self.current_fields

        field_attribute = 'list_{}_{}_fields'.format(self.kwargs.get('app'), self.kwargs.get('model'))
        current_fields = self.request.user.attributes.get_attribute(field_attribute, [])
        request_fields = self.request.POST.get('selected_fields', None)

        if request_fields and ','.join(current_fields) != request_fields:
            # TODO validate fields
            current_fields = request_fields.split(',')
            self.request.user.attributes.set_attribute(field_attribute, current_fields)

        if not current_fields:
            current_fields = ['created_at', 'id']

        self.current_fields = current_fields
        return current_fields

    def get_items(self, model, paginator, current_page):
        config = models_config.get_config(model)
        fields = config.get_list_fields()

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

    def get_paginator(self, model):
        query = self.search_queryset(model)
        # TODO Apply filters
        query = query.order_by(self.get_sort())

        return Paginator(query, self.get_page_size())

    def search_queryset(self, model):
        config = models_config.get_config(model)
        queryset = model.objects.get_queryset()

        if config.list_select_related:
            queryset = queryset.select_related(*config.list_select_related)

        # get search field config
        def construct_search(field_name):
            if field_name.startswith('^'):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        search = self.get_search()
        if config.list_search_fields and search:
            orm_lookups = [construct_search(field) for field in config.list_search_fields]

            for bit in search.split():
                or_queries = [Q(**{orm_lookup: bit}) for orm_lookup in orm_lookups]
                queryset = queryset.filter(reduce(operator.or_, or_queries))

        return queryset

    def get_and_save_value(self, name, default=None):
        if getattr(self, name, None):
            return getattr(self, name)

        value = self.get_session_value(name, default)
        value = self.request.POST.get(name, value)
        self.save_value(name, value)
        return value

    def get_session_value(self, name, default=None):
        session_name = 'list_{}_{}_{}'.format(self.kwargs.get('app'), self.kwargs.get('model'), name)
        return self.request.session.get(session_name, default)

    def save_value(self, name, value):
        session_name = 'list_{}_{}_{}'.format(self.kwargs.get('app'), self.kwargs.get('model'), name)
        self.request.session[session_name] = value
        setattr(self, name, value)
        return value


class DetailTabView(DetailView, SingleUrlObjectMixin):
    """
    Detail tab view, shows model details in tab view
    """

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
        """
        Get queryset based on url params(<app>, <mode>) if model is not set on class
        """
        if self.queryset is None and not self.model:
            try:
                ModelClass = apps.get_model(self.kwargs.get('app'), self.kwargs.get('model'))
                return ModelClass._default_manager.all()
            except LookupError:
                raise Http404()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tabs = self.get_active_tabs()
        context.update({
            'page_detail_tabs': tabs,
            'active_tab': tabs[0].code if tabs else '',
            'app_label': self.get_app_label(),
            'model_name': self.get_model_name(),
            'model_alias': self.model_alias,
            'model_verbose_name': self.object._meta.verbose_name.title(),
            'back_url': self.get_back_url(),
            'edit_url': self.get_edit_url(),
            'delete_url': self.get_delete_url(),
            'title': self.title,
        })
        return context

    def get_back_url(self):
        return ''

    def get_delete_url(self):
        return reverse('trionyx:model-delete', kwargs={
            'app': self.get_app_label(),
            'model': self.get_model_name(),
            'pk': self.object.id
        })

    def get_edit_url(self):
        return reverse('trionyx:model-edit', kwargs={
            'app': self.get_app_label(),
            'model': self.get_model_name(),
            'pk': self.object.id
        })

    def get_app_label(self):
        return self.object._meta.app_label

    def get_model_name(self):
        return self.object._meta.model_name

    def get_active_tabs(self):
        if self.model_alias:
            return list(Tab.get_tabs(self.model_alias, self.object))
        else:
            return list(Tab.get_tabs('{}.{}'.format(self.get_app_label(), self.get_model_name()), self.object))

    def dispatch(self, request, *args, **kwargs):
        if False:  # TODO do permission check based on Model
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class DetailTabJsendView(JsendView):
    """
    View for getting tab view with ajax
    """

    def handle_request(self, request, app, model, pk):
        ModelClass = apps.get_model(app, model)
        object = ModelClass.objects.get(id=pk)

        tab_code = request.GET.get('tab')
        model_alias = request.GET.get('model_alias')
        model_alias = model_alias if model_alias else '{}.{}'.format(app, model)

        # TODO permission check

        item = Tab.get_tab(model_alias, object, tab_code)

        return item.get_layout(object).render(request)


class UpdateView(DjangoUpdateView, SingleUrlObjectMixin):
    """Update view that renders view with crispy-forms"""

    template_name = 'trionyx/core/model_update.html'

    title = None
    """Title of page, default is: Update <object.__str__>"""

    submit_value = None
    """Value of the form submit button"""

    cancel_url = None
    """Url code for cancel button, when not set object.get_absolute_url is used"""

    def get_queryset(self):
        """
        Get queryset based on url params(<app>, <mode>) if model is not set on class
        """
        if self.queryset is None and not self.model:
            try:
                ModelClass = apps.get_model(self.kwargs.get('app'), self.kwargs.get('model'))
                return ModelClass._default_manager.all()
            except LookupError:
                raise Http404()
        return super().get_queryset()

    def get_form_class(self):
        if self.form_class:
            return self.form_class
        config = models_config.get_config(self.get_model_class())
        return config.get_edit_form()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if not getattr(form, 'helper', None):
            form.helper = FormHelper()
            form.helper.form_tag = False
        else:
            form.helper.form_tag = False
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            'submit_value': self.submit_value,
            'cancel_url': self.cancel_url,
        })

        return context

    def dispatch(self, request, *args, **kwargs):
        if False:  # TODO do permission check based on Model
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class CreateView(DjangoCreateView, SingleUrlObjectMixin):
    """Create view that renders view with crispy-forms"""

    template_name = 'trionyx/core/model_create.html'

    title = None
    """Title of page, default is: Update <object.__str__>"""

    submit_value = None
    """Value of the form submit button"""

    cancel_url = None
    """Url code for cancel button, when not set model list view is used"""

    def get_queryset(self):
        """
        Get queryset based on url params(<app>, <mode>) if model is not set on class
        """
        if self.queryset is None and not self.model:
            try:
                ModelClass = apps.get_model(self.kwargs.get('app'), self.kwargs.get('model'))
                return ModelClass._default_manager.all()
            except LookupError:
                raise Http404()
        return super().get_queryset()

    def get_form_class(self):
        if self.form_class:
            return self.form_class
        config = models_config.get_config(self.get_model_class())
        return config.get_create_form()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if not getattr(form, 'helper', None):
            form.helper = FormHelper()
            form.helper.form_tag = False
        else:
            form.helper.form_tag = False
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            'submit_value': self.submit_value,
            'cancel_url': self.cancel_url,
            'model_verbose_name': self.get_model_class()._meta.verbose_name
        })

        return context

    def dispatch(self, request, *args, **kwargs):
        if False:  # TODO do permission check based on Model
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class DeleteView(DjangoDeleteView):
    """Delete view"""

    template_name = 'trionyx/core/model_delete.html'

    title = None
    """Title of page, default is: Update <object.__str__>"""

    submit_value = None
    """Value of the form submit button"""

    cancel_url = None
    """Url code for cancel button, when not set model list view is used"""

    def get_queryset(self):
        """
        Get queryset based on url params(<app>, <mode>) if model is not set on class
        """
        if self.queryset is None and not self.model:
            try:
                ModelClass = apps.get_model(self.kwargs.get('app'), self.kwargs.get('model'))
                return ModelClass._default_manager.all()
            except LookupError:
                raise Http404()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            'submit_value': self.submit_value,
            'cancel_url': self.cancel_url
        })
        return context

    def get_success_url(self):
        if self.success_url:
            return reverse(self.success_url)
        return '/'  # TODO go to list view

    def dispatch(self, request, *args, **kwargs):
        if False:  # TODO do permission check based on Model
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
