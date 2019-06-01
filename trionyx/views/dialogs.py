"""
trionyx.views.dialogs
~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""

from django.views.generic import View
from django.http import JsonResponse
from django.template.loader import render_to_string

from trionyx.views.mixins import ModelClassMixin
from trionyx.forms.helper import FormHelper


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

    permission_type = 'view'
    """Permission type used for model when no permission is set"""

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
            config = self.get_model_config()
            return request.user.has_perm('{app_label}.{type}_{model_name}'.format(
                app_label=config.app_label,
                type=self.permission_type,
                model_name=config.model_name,
            ).lower())

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


class LayoutDialog(DialogView):
    """Render layout in dialog"""

    def display_dialog(self, code):
        """Render layout for object"""
        from trionyx.views import layouts
        try:
            content = layouts.get_layout(code, self.object, self.request)
        except Exception:
            content = 'Layout does not exists'

        return {
            'title': str(self.object),
            'content': content,
        }


class UpdateDialog(DialogView):
    """Update dialog view for updating a model"""

    permission_type = 'change'

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
        from trionyx.forms import form_register
        if self.kwargs.get('code'):
            return form_register.get_form(self.get_model_class(), self.kwargs.get('code'))
        return form_register.get_edit_form(self.get_model_class())

    def display_dialog(self, *args, **kwargs):
        """Display form and success message when set"""
        form = kwargs.pop('form_instance', None)
        success_message = kwargs.pop('success_message', None)

        if not form:
            form = self.get_form_class()(initial=kwargs, instance=self.object)

        if not hasattr(form, "helper"):
            form.helper = FormHelper(form)
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

    permission_type = 'add'

    title = "Create {model_name}"
    submit_label = 'create'
    success_message = '{model_name} ({object}) is successfully created'

    def get_form_class(self):
        """Get create form class"""
        from trionyx.forms import form_register
        if self.kwargs.get('code'):
            return form_register.get_form(self.get_model_class(), self.kwargs.get('code'))
        return form_register.get_create_form(self.get_model_class())


class DeleteDialog(DialogView):
    """Delete model dialog"""

    permission_type = 'delete'

    template = 'trionyx/dialog/model_delete.html'
    """Template for dialog content"""

    title = "Delete {model_name}: {object}"
    """Dialog title model_name and object, variable are given"""

    submit_label = 'delete'
    """Dialog submit label value"""

    success_message = '{model_name} ({object}) is successfully deleted'
    """Success message on successfully deleted"""

    def display_dialog(self, *args, **kwargs):
        """Display delete confirmation"""
        return {
            'title': self.title.format(
                model_name=self.get_model_config().model_name,
                object=str(self.object),
            ),
            'content': self.render_to_string(self.template, {
                'model_name': self.get_model_config().model_name.capitalize(),
                'object': self.object,
            }),
            'submit_label': self.submit_label,
        }

    def handle_dialog(self, *args, **kwargs):
        """Handle delete model"""
        object_name = str(self.object)
        response = {
            'title': self.title.format(
                model_name=self.get_model_config().model_name,
                object=object_name,
            ),
        }

        try:
            self.object.delete()
            response.update({
                'content': self.success_message.format(
                    model_name=self.get_model_config().model_name.capitalize(),
                    object=object_name,
                )
            })
        except Exception:
            response.update({
                'content': """<p class="alert alert-danger">Something went wrong on deleting {}</p>""".format(
                    self.get_model_config().model_name.capitalize()
                )
            })

        return response
