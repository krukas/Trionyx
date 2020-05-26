"""
trionyx.trionyx.api.routers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2019 by Maikel Martens
:license: GPLv3
"""
from importlib import import_module

from django.apps import apps
from rest_framework import routers
from rest_framework import serializers
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet

from trionyx.config import models_config
from trionyx.forms import form_register
from trionyx.api.serializers import serializer_register


class AutoRouter(routers.DefaultRouter):
    """Auto router for adding all models to REST API"""

    @staticmethod
    def get_model_prefix(model):
        """Get model API prefix"""
        app_label = model._meta.app_label.replace(' ', '_').lower()
        model_name = model.__name__.lower()
        return '{}/{}'.format(app_label, model_name)

    def __init__(self):
        """Init class and find all model routes"""
        super(AutoRouter, self).__init__()
        self.app_ready = False

    @property
    def urls(self):
        """Get API urls"""
        if not self.app_ready:
            return []

        if not hasattr(self, '_urls'):
            self.auto_regiser_models()
            self.register_apps()
            self._urls = self.get_urls()

        return self._urls

    def __len__(self):
        """Get length of urls"""
        return len(self.urls)

    def __getitem__(self, index):
        """Get url item"""
        return self.urls[index]

    def register_apps(self):
        """Register all API views from apps that are exported to routes.py"""
        for app in apps.get_app_configs():
            try:
                routes = import_module('{}.routes'.format(app.module.__package__))
            except (ImportError, TypeError):
                try:  # Fallback mode
                    routes = import_module('{}.routes'.format('.'.join(app.module.__package__.split('.')[:-2])))
                except (ImportError, TypeError):
                    continue

            if hasattr(routes, 'apiroutes'):
                for route in getattr(routes, 'apiroutes'):
                    self.register(**route)

    def auto_regiser_models(self):
        """Auto register all models"""
        # Load serializers
        for app in apps.get_app_configs():
            for module in ['serializers', 'api.serializers']:
                try:
                    import_module('{}.{}'.format(app.module.__package__, module))
                except ImportError:
                    pass

        for config in models_config.get_all_configs():
            if config.api_disable:
                continue

            model = config.model
            basename = model._meta.object_name.lower()
            classname = model.__name__
            serializer = serializer_register.get(model)

            DynamicViewSet = type(
                classname,
                (ModelViewSet,),
                {}
            )
            DynamicViewSet.model = model
            DynamicViewSet.queryset = model.objects.get_queryset()
            DynamicViewSet.serializer_class = serializer if serializer else self.generate_model_serializer(model, config)
            DynamicViewSet.permission_classes = (ExtendedDjangoModelPermissions,)
            DynamicViewSet.ordering = ['pk']

            # TODO maybe add serializer switcher https://www.django-rest-framework.org/api-guide/generic-views/#get_serializer_classself
            # So all API endpoint are read only but you can only see id and verbose name

            self.register(self.get_model_prefix(model), DynamicViewSet, basename)

    def generate_model_serializer(self, model, config):
        """Generate a model serializer with all fields"""
        class MetaModelSerializer(serializers.ModelSerializer):
            """Meta model serializer to make all fields work"""

            class Meta:
                model = None
                fields = None
                read_only_fields = None

        fields = []
        if config.api_fields:
            fields = config.api_fields
        else:
            for form in form_register.get_all_forms(model):
                fields.extend([name for name in form.base_fields])

        model_fields = [field.name for field in config.get_fields(True, True)]
        MetaModelSerializer.Meta.fields = [field for field in model_fields]
        MetaModelSerializer.Meta.read_only_fields = list({'id', 'created_at', 'updated_at', 'verbose_name', *[
            field for field in model_fields if field not in fields
        ]})

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
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
    }


def router(prefix, viewset, basename):
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
        'basename': basename
    }
