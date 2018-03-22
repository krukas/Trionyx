from django.views.generic.edit import UpdateView as DjangoUpdateView
from django.core.exceptions import PermissionDenied

from crispy_forms.helper import FormHelper


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
        return super(UpdateView, self).dispatch(request, *args, **kwargs)