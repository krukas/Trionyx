"""
trionyx.routers
~~~~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
from importlib import import_module

import django
from django.conf import settings
from rest_framework import routers
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from rest_framework.permissions import DjangoModelPermissions

from trionyx.core.models import BaseManager


class AutoRouter(routers.DefaultRouter):
    """Auto router for adding all models to REST API"""

    @staticmethod
    def get_model_prefix(model):
        """Get model API prefix"""
        app_label = model._meta.app_label.replace(' ', '_').lower()
        model_name = model.__name__.lower()
        return 'models/{}/{}'.format(app_label, model_name)

    def __init__(self):
        """Init class and find all model routes"""
        super(AutoRouter, self).__init__()
        self.auto_regiser_models()
        self.register_apps()

    def register_apps(self):
        """Register all API views from apps that are exported to routes.py"""
        for app in settings.INSTALLED_APPS:
            try:
                routes = import_module('{}.routes'.format(app))
            except (ImportError, TypeError):
                try:  # Fallback mode
                    routes = import_module('{}.routes'.format('.'.join(app.split('.')[:-2])))
                except (ImportError, TypeError):
                    continue

            if hasattr(routes, 'apiroutes'):
                for route in getattr(routes, 'apiroutes'):
                    self.register(**route)

    def auto_regiser_models(self):
        """Auto register all models"""
        for model in django.apps.apps.get_models():
            full_class_name = '{}.{}'.format(model.__module__, model.__name__)
            if full_class_name in BaseManager.ignore_models:
                continue

            if hasattr(model, 'NO_API') and getattr(model, 'NO_API'):
                continue

            basename = model._meta.object_name.lower()
            classname = model.__name__

            DynamicViewSet = type(
                classname,
                (ModelViewSet,),
                {}
            )
            DynamicViewSet.model = model
            DynamicViewSet.queryset = model.objects.get_queryset()
            DynamicViewSet.serializer_class = self.generate_model_serializer(model)
            DynamicViewSet.permission_classes = (ExtendedDjangoModelPermissions,)

            if hasattr(model, 'search_fields'):
                DynamicViewSet.search_fields = [x.split(':')[0] for x in model.search_fields]

            self.register(self.get_model_prefix(model), DynamicViewSet, basename)

    def generate_model_serializer(self, model):
        """Generate a model serializer with all fields"""
        # TODO on model level set which fields to serialize

        class MetaModelSerializer(serializers.ModelSerializer):
            """Meta model serializer to make all fields work"""

            class Meta:
                model = None
                fields = '__all__'

        DynamicSerializer = type(
            '{}Serializer'.format(model.__name__),
            (MetaModelSerializer,),
            {}
        )
        DynamicSerializer.Meta.model = model

        return DynamicSerializer


class ExtendedDjangoModelPermissions(DjangoModelPermissions):
    """Permission class that added read as permission"""

    perms_map = {
        'GET': ['%(app_label)s.read_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
    }


def router(prefix, viewset, base_name):
    """
    Define an API route

    :param prefix:
    :param viewset:
    :param base_name:
    :return:
    """
    return {
        'prefix': prefix,
        'viewset': viewset,
        'base_name': base_name
    }
