"""
trionyx.core.api
~~~~~~~~~~~~~~~~

Core api views

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import Permission

from trionyx.views import ModelView
from trionyx.navigation import Menu

from .models import BaseManager


class PermissionTreeViewSet(viewsets.ViewSet):
    """API to Retrive all permission Tree"""

    ignore_models = [
        'django.contrib.auth.models.Permission',
        'django.contrib.sessions.models.Session',
        'django.contrib.contenttypes.models.ContentType',
        'django.contrib.admin.models.LogEntry',
        'rest_framework.authtoken.models.Token',
    ]

    def list(self, request, *args, **kwargs):
        """Get tree from all permissions"""
        # TODO: add permission check

        tree = []
        models = []
        model_permissions = []

        current_app_name = None
        current_model_name = None

        for permission in Permission.objects.select_related('content_type').order_by('content_type__app_label',
                                                                                     'content_type__model', 'name'):
            model_class = permission.content_type.model_class()
            app_name = permission.content_type.app_label
            model_name = permission.content_type.model

            BaseManager.is_active_model(permission.content_type.model_class())
            if not model_class:
                continue

            full_class_name = '{}.{}'.format(
                permission.content_type.model_class().__module__,
                permission.content_type.model_class().__name__)

            if full_class_name in self.ignore_models:
                continue

            if not current_app_name or current_app_name != app_name:
                if current_app_name:
                    tree.append({
                        'id': None,
                        'name': current_app_name,
                        'children': models,
                    })
                current_app_name = app_name
                models = []

            if not current_model_name or current_model_name != model_name:
                if current_model_name:
                    models.append({
                        'id': None,
                        'name': current_model_name,
                        'children': model_permissions,
                    })
                current_model_name = model_name
                model_permissions = []

            model_permissions.append({
                'id': permission.id,
                'name': permission.name,
            })

        models.append({
            'id': None,
            'name': current_model_name,
            'children': model_permissions,
        })
        tree.append({
            'id': None,
            'name': current_app_name,
            'children': models,
        })

        return Response(tree, status=status.HTTP_200_OK)


class ModelDefinitionsViewSet(viewsets.ViewSet):
    """Api view for model definitions"""

    def list(self, request, *args, **kwargs):
        """Give list of model definitions"""
        return Response(BaseManager.get, status=status.HTTP_200_OK)


class ModelViewsViewSet(viewsets.ViewSet):
    """Api view for model views"""

    def list(self, request, *args, **kwargs):
        """Give list of model views"""
        return Response(ModelView.get_config(), status=status.HTTP_200_OK)


class ApplicationConfigViewSet(viewsets.ViewSet):
    """Api view for application config"""

    def list(self, request, *args, **kwargs):
        """Give list of application configs"""
        return Response({}, status=status.HTTP_200_OK)


class ApplicationMenuViewSet(viewsets.ViewSet):
    """Api view for application menu"""

    def list(self, request, *args, **kwargs):
        """Give application menu tree"""
        return Response(Menu.get_config(), status=status.HTTP_200_OK)
