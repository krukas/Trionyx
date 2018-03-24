from django.apps import apps
from django.views.generic import DetailView, UpdateView as DjangoUpdateView
from django.core.exceptions import PermissionDenied
from django_jsend import JsendView

from crispy_forms.helper import FormHelper

from trionyx.navigation import Tab


class DetailTabView(DetailView):
    """
    Detail tab view, shows model details in tab view
    """

    template_name = "trionyx/core/detail_tab_view.html"
    """Template name for rendering the view, default is 'trionyx/core/detail_tab_view.html'

        .. note::
            Only overide this if you want to customize the layout of the page.
    """

    model_alias = None
    """Model identifier, default is '<model app name>.<model name>'."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_detail_tabs'] = self.get_active_tabs()
        context['active_tab'] = context['page_detail_tabs'][0].code
        context['app_label'] = self.get_app_label()
        context['model_name'] = self.get_model_name()
        context['model_alias'] = self.model_alias
        return context

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


class UpdateView(DjangoUpdateView):
    """Update view that renders view with crispy-forms"""

    template_name = 'trionyx/core/update_model.html'

    title = None
    """Title of page, default is: Update <object.__str__>"""

    submit_value = None
    """Value of the form submit button"""

    cancel_url = None
    """Url code for cancel butten, when not set cancel butten is not shown"""

    def get_form(self):
        form = super().get_form()
        if not getattr(form, 'helper', None):
            form.helper = FormHelper()
            form.helper.form_tag = False
        else:
            form.helper.form_tag = False
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['submit_value'] = self.submit_value
        context['cancel_url'] = self.cancel_url
        return context

    def dispatch(self, request, *args, **kwargs):
        if False: # TODO do permission check based on Model
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)