"""
trionyx.views.dialogs
~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import logging
import json
from typing import Optional, Dict, Any, Type

from django.views.generic import View
from django.http import JsonResponse
from django.http.request import HttpRequest
from django.http import Http404
from django.template.loader import render_to_string
from django.db.models import Model
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from trionyx.views.mixins import ModelClassMixin
from trionyx.forms.helper import FormHelper

logger = logging.getLogger(__name__)


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

    permission_type: str = 'view'
    """Permission type used for model when no permission is set"""

    permission: Optional[str] = None
    """Permission of dialog, when not set and model is set model view permission is used"""

    model_permission: str = 'read'
    """When no permission is set will use this for model permission"""

    model: Optional[Type[Model]] = None
    """
    Model that will be auto loaded, when set the url mus contain a `pk` parameter.
    Model can also be set with the url with the `app` and `model` parameter.

    Loaded model object is available as self.object and self.<object name lowercase>
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        """Handle get request"""
        try:
            self.load_object(kwargs)
        except Exception as e:
            return self.render_te_response({
                'title': str(e),
            })

        if not self.has_permission(request):
            return self.render_te_response({
                'title': _('No access'),
            })
        return self.render_te_response(self.display_dialog())

    def post(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        """Handle post request"""
        try:
            self.load_object(kwargs)
        except Exception as e:
            return self.render_te_response({
                'title': str(e),
            })

        if not self.has_permission(request):
            return self.render_te_response({
                'title': _('No access'),
            })
        return self.render_te_response(self.handle_dialog())

    def load_object(self, kwargs):
        """Load object and model config and remove pk from kwargs"""
        self.object = None
        self.config = None
        try:
            self.model = self.get_model_class()
        except Http404 as e:
            if self.model or ('app' in self.kwargs and 'model' in self.kwargs):
                raise e
            return kwargs

        if self.model and kwargs.get('pk', False):
            try:
                self.object = self.model.objects.get(pk=kwargs.get('pk'))
            except Exception:
                raise Exception(_("Could not load {model}").format(model=self.model.__name__.lower()))
            setattr(self, self.model.__name__.lower(), self.object)

        return kwargs

    def has_permission(self, request: HttpRequest) -> bool:
        """Check if user has permission"""
        if not self.object and not self.permission and self.permission_type != 'add':
            return True

        if not self.permission:
            return self.get_model_config().has_permission(
                self.permission_type,
                self.object,
                request.user
            )

        return request.user.has_perm(self.permission)

    def render_to_string(self, template_file: str, context: Dict[str, Any]) -> str:
        """Render given template to string and add object to context"""
        context = context if context else {}
        if self.object:
            context['object'] = self.object
            context[self.object.__class__.__name__.lower()] = self.object
        return render_to_string(template_file, context, self.request)

    def display_dialog(self) -> Dict[str, Any]:
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
        raise NotImplementedError

    def handle_dialog(self) -> Dict[str, Any]:
        """
        Override this function to handle and display popup. Url params are given as function params.
        This function must return the same dict structure as :class:`trionyx.trionyx.views.core.DialogView.display_dialog`

        Post data can be retrieved with *self.request.POST*
        """
        raise NotImplementedError

    def render_te_response(self, data: Dict[str, Any]) -> JsonResponse:
        """Render data to JsonResponse"""
        if 'submit_label' in data and 'url' not in data:
            data['url'] = self.request.get_full_path()

        return JsonResponse(data)


class LayoutDialog(DialogView):
    """Render layout in dialog"""

    def display_dialog(self) -> Dict[str, Any]:
        """Render layout for object"""
        from trionyx.views import layouts
        try:
            content = layouts.get_layout(self.kwargs.get('code'), self.object).render(self.request)
        except Exception:
            content = _('Layout does not exists')

        return {
            'title': str(self.object),
            'content': content,
        }


class UpdateDialog(DialogView):
    """Update dialog view for updating a model"""

    permission_type = 'change'

    template = 'trionyx/dialog/model_form.html'
    """Template for dialog content"""

    title = _("Update {model_name}: {object}")
    """Dialog title model_name and object, variable are given"""

    submit_label = _('save')
    """Dialog submit label value"""

    success_message = _('{model_name} ({object}) is successfully updated')
    """Success message on successfully form saved"""

    def get_form_class(self) -> Type[ModelForm]:
        """Get form class for dialog, default will get form from model config"""
        from trionyx.forms import form_register
        if self.kwargs.get('code'):
            return form_register.get_form(self.get_model_class(), self.kwargs.get('code'))
        return form_register.get_edit_form(self.get_model_class())

    def display_dialog(self, form: Optional[ModelForm] = None, success_message: Optional[str] = None) -> Dict[str, Any]:
        """Display form and success message when set"""
        initial = {
            **{key: value for key, value in self.request.GET.items()},
        }

        if not form:
            form = self.get_form_class()(initial=initial, instance=self.object)

        helper = getattr(form, 'helper', FormHelper(form))
        helper.form_tag = False
        setattr(form, 'helper', helper)

        return {
            'title': form.get_title() if hasattr(form, 'get_title') else self.title.format(  # type: ignore
                model_name=self.get_model_config().model_name,
                object=str(self.object) if self.object else '',
            ),
            'content': self.render_to_string(self.template, {
                'form': form,
                'success_message': success_message,
            }),
            'submit_label': form.get_submit_label() if hasattr(form, 'get_submit_label') else self.submit_label,  # type: ignore
            'success': bool(success_message),
        }

    def handle_dialog(self) -> Dict[str, Any]:
        """Handle form and save and set success message on valid form"""
        form = self.get_form_class()(data=self.request.POST, files=self.request.FILES, instance=self.object)

        success_message = None
        if form.is_valid():
            obj = form.save()
            success_message = self.success_message.format(
                model_name=self.get_model_config().get_verbose_name(),
                object=str(obj),
            )
        else:
            logger.debug(json.dumps(form.errors))

        return self.display_dialog(form=form, success_message=success_message)


class CreateDialog(UpdateDialog):
    """Dialog view for creating a model"""

    permission_type = 'add'

    title = _("Create {model_name}")
    submit_label = _('create')
    success_message = _('{model_name} ({object}) is successfully created')

    def get_form_class(self) -> Type[ModelForm]:
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

    title = _("Delete {model_name}: {object}")
    """Dialog title model_name and object, variable are given"""

    submit_label = _('delete')
    """Dialog submit label value"""

    success_message = _('{model_name} ({object}) is successfully deleted')
    """Success message on successfully deleted"""

    def display_dialog(self) -> Dict[str, Any]:
        """Display delete confirmation"""
        return {
            'title': self.title.format(
                model_name=self.get_model_config().model_name,
                object=str(self.object),
            ),
            'content': self.render_to_string(self.template, {
                'model_name': self.get_model_config().get_verbose_name(),
                'object': self.object,
            }),
            'submit_label': self.submit_label,
        }

    def handle_dialog(self) -> Dict[str, Any]:
        """Handle delete model"""
        object_name = str(self.object)
        response: Dict[str, Any] = {
            'title': self.title.format(
                model_name=self.get_model_config().model_name,
                object=object_name,
            ),
        }

        try:
            self.object.delete()
            response.update({
                'content': self.success_message.format(
                    model_name=self.get_model_config().get_verbose_name(),
                    object=object_name,
                ),
                'success': True,
            })
        except Exception:
            response.update({
                'content': """<p class="alert alert-danger">{}</p>""".format(
                    _('Something went wrong on deleting {model_name}').format(
                        model_name=self.get_model_config().get_verbose_name())
                ),
                'success': False,
            })

        return response
