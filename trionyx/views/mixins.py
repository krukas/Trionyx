"""
trionyx.views.mixins
~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from typing import Optional, Type, Any

from django.apps import apps
from django.db.models import Model
from django.http.request import HttpRequest
from django.core.exceptions import PermissionDenied
from django.http import Http404

from trionyx.config import models_config, ModelConfig


class ModelClassMixin:
    """Mixen for getting model class"""

    def get_model_class(self) -> Optional[Type[Model]]:
        """Get model class"""
        kwargs = getattr(self, 'kwargs', {})

        if getattr(self, 'model', None):
            return getattr(self, 'model')
        elif getattr(self, 'object', None):
            return getattr(self, 'object').__class__
        elif 'app' in kwargs and 'model' in kwargs:
            try:
                return apps.get_model(kwargs.get('app'), kwargs.get('model'))  # type: ignore
            except LookupError:
                raise Http404()
        elif hasattr(self, 'get_queryset'):
            return self.get_queryset().model  # type: ignore
        else:
            raise Http404()

    def get_model_config(self) -> ModelConfig:
        """Get Trionyx model config"""
        ModelClass = self.get_model_class()
        if not ModelClass:
            raise Exception('Could not get model class')

        if not hasattr(self, '__config'):
            setattr(self, '__config', models_config.get_config(ModelClass))
        return getattr(self, '__config', None)


class ModelPermissionMixin:
    """Check Model permission"""

    permission_type: Optional[str] = None

    def get_object(self, *args, **kwargs):
        """Override to prevent multiple lookups"""
        if not getattr(self, 'object', False) and hasattr(super(), 'get_object'):
            self.object = getattr(super(), 'get_object', lambda *args, **kwargs: None)(*args, **kwargs)
        return getattr(self, 'object', None)

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        """Validate if user can use view"""
        if self.permission_type in ['view', 'add', 'change', 'delete'] and hasattr(self, 'get_model_config'):
            try:
                obj = self.get_object()
            except AttributeError:
                obj = None
            if not self.get_model_config().has_permission(self.permission_type, obj, request.user):  # type: ignore
                raise PermissionDenied()
        elif self.permission and not request.user.has_perm(self.permission):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)  # type: ignore

    @property
    def permission(self) -> Optional[str]:
        """Permission for view"""
        if self.permission_type and hasattr(self, 'get_model_config'):
            config = self.get_model_config()  # type: ignore

            return '{app_label}.{type}_{model_name}'.format(
                app_label=config.app_label,
                type=self.permission_type,
                model_name=config.model_name,
            ).lower()
        return None


class SessionValueMixin:
    """Mixin for handling session values"""

    def get_and_save_value(self, name: str, default: Any = None) -> Any:
        """Get value from request/session and save value to session"""
        request: HttpRequest = getattr(self, 'request')

        if getattr(self, name, None):
            return getattr(self, name)

        value = self.get_session_value(name, default)
        value = request.POST.get(name, value)
        self.save_value(name, value)
        return value

    def get_session_value(self, name: str, default: Any = None) -> Any:
        """Get value from session"""
        kwargs = getattr(self, 'kwargs', {})
        request: HttpRequest = getattr(self, 'request')
        session_name = 'list_{}_{}_{}'.format(kwargs.get('app'), kwargs.get('model'), name)
        return request.session.get(session_name, default)

    def save_value(self, name: str, value: Any) -> Any:
        """Save value to session"""
        kwargs = getattr(self, 'kwargs', {})
        request: HttpRequest = getattr(self, 'request')
        session_name = 'list_{}_{}_{}'.format(kwargs.get('app'), kwargs.get('model'), name)
        request.session[session_name] = value
        setattr(self, name, value)
        return value
