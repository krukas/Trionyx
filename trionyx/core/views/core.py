from django.apps import apps
from django.views.generic import DetailView, UpdateView as DjangoUpdateView, CreateView as DjangoCreateView, DeleteView as DjangoDeleteView
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django_jsend import JsendView
from django.urls import reverse
from django.contrib import messages # TODO add success message to create/edit/delete

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
        if False: # TODO do permission check based on Model
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
        if False: # TODO do permission check based on Model
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
        return '/' # TODO go to list view

    def dispatch(self, request, *args, **kwargs):
        if False:  # TODO do permission check based on Model
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)