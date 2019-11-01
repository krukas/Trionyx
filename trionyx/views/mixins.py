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
            return apps.get_model(kwargs.get('app'), kwargs.get('model'))  # type: ignore
        elif hasattr(self, 'get_queryset'):
            return self.get_queryset().model  # type: ignore
        else:
            return None

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

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        """Validate if user can use view"""
        if not self.is_enabled() or (self.permission and not request.user.has_perm(self.permission)):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)  # type: ignore

    def is_enabled(self) -> bool:
        """Check if permission type is enabled for model"""
        if not hasattr(self, 'get_model_config'):
            return True

        if self.permission_type == 'change' and self.get_model_config().disable_change:  # type: ignore
            return False

        if self.permission_type == 'add' and self.get_model_config().disable_add:  # type: ignore
            return False

        if self.permission_type == 'delete' and self.get_model_config().disable_delete:  # type: ignore
            return False

        return True

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
