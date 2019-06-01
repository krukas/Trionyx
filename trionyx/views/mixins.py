"""
trionyx.views.mixins
~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from django.apps import apps
from django.core.exceptions import PermissionDenied

from trionyx.config import models_config


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


class ModelPermissionMixin:
    """Check Model permission"""

    permission_type = None

    def dispatch(self, request, *args, **kwargs):
        """Validate if user can use view"""
        if self.permission and not request.user.has_perm(self.permission):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    @property
    def permission(self):
        """Permission for view"""
        if self.permission_type and hasattr(self, 'get_model_config'):
            config = self.get_model_config()
            return '{app_label}.{type}_{model_name}'.format(
                app_label=config.app_label,
                type=self.permission_type,
                model_name=config.model_name,
            ).lower()
        return None


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
