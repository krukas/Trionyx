"""
trionyx.trionyx.api.routers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2019 by Maikel Martens
:license: GPLv3
"""
from importlib import import_module
from collections import defaultdict

from django.apps import apps
from rest_framework import routers
from rest_framework import serializers
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet, mixins, GenericViewSet
from rest_framework.schemas.openapi import AutoSchema, SchemaGenerator, is_list_view
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from trionyx.config import models_config
from trionyx.forms import form_register
from trionyx.api.serializers import serializer_register
from trionyx.trionyx.conf import settings as tx_settings


class APISchemaGenerator(SchemaGenerator):
    """Schema generator"""

    @property
    def title(self):
        """Get API title"""
        return f'{tx_settings.APP_NAME} API'

    @title.setter
    def title(self, value):
        """Set API title"""
        pass

    def get_schema(self, *args, **kwargs):
        """Extend schema"""
        schema = super().get_schema(*args, **kwargs)
        schema['components'] = {
            'securitySchemes': {
                "Api token": {
                    "type": "apiKey",
                    "name": "Authorization",
                    "in": "header",
                    "bearerFormat": 'Token',
                    'description': """{}

    Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b""".format(
                        _('The key should be prefixed by the string literal **"Token"**, with whitespace separating the two strings. For example:'), # noqa E501
                    ),
                },
            }
        }

        groups = defaultdict(list)
        for config in models_config.get_all_configs():
            if config.api_disable:
                continue

            group_name = str(config.app_config.verbose_name)
            groups[group_name].append(config.get_verbose_name_plural(True))
            groups[group_name].sort()

        # TODO for custom views: add user defined groups and add custom tag to existing group
        schema['x-tagGroups'] = [
            {
                'name': name,
                'tags': groups[name],
            } for name in sorted(groups)
        ]

        return schema

    def has_view_permissions(self, *args, **kwargs):
        """Enable generate complete schema"""
        return True


class APIAutoSchema(AutoSchema):
    """Auto view schema"""

    translate_mapping = {
        'get': _('Retrieve'),
        'post': _('Add'),
        'put': _('Update'),
        'patch': _('Partial update'),
        'delete': _('Delete'),
        'list': _('List'),
        'retrieve': _('Retrieve'),
        'create': _('Add'),
        'update': _('Update'),
        'partial_update': _('Partial update'),
        'destroy': _('Delete'),
    }

    def __init__(self, tags=None):
        """Init Schema"""
        super().__init__()
        self.tags = tags if tags else []

    def get_operation(self, path, method):
        """Get operation"""
        operation = super().get_operation(path, method)
        operation['summary'] = self._get_operation_summary(path, method)
        operation['tags'] = self.tags
        operation['x-codeSamples'] = self._get_operation_code_samples(path, method)
        return operation

    def get_description(self, *args, **kwargs):
        """Get api description"""
        model = getattr(getattr(self.view, 'queryset', None), 'model', None)
        if model:
            config = models_config.get_config(model)
            if config.api_description:
                return config.api_description

        return super().get_description(*args, **kwargs)

    def _get_operation_summary(self, path, method):
        """Get operation id"""
        method_name = getattr(self.view, 'action', method.lower())
        if is_list_view(path, method, self.view):
            action = _('List')
        elif method_name not in self.translate_mapping:
            action = method_name
        else:
            action = self.translate_mapping[method.lower()]

        model = getattr(getattr(self.view, 'queryset', None), 'model', None)
        if model:
            config = models_config.get_config(model)
            name = config.get_verbose_name_plural(title=True) if action == 'list' else config.get_verbose_name(title=True)
        else:
            if hasattr(self.view, 'get_serializer_class'):
                name = self.view.get_serializer_class().__name__
                if name.endswith('Serializer'):
                    name = name[:-10]

                # Fallback to the view name
            else:
                name = self.view.__class__.__name__
                if name.endswith('APIView'):
                    name = name[:-7]
                elif name.endswith('View'):
                    name = name[:-4]

                # Due to camel-casing of classes and `action` being lowercase, apply title in order to find if action truly
                # comes at the end of the name
                if name.endswith(action.title()):  # ListView, UpdateAPIView, ThingDelete ...
                    name = name[:-len(action)]

        return f'{action} {name}'

    def _get_operation_code_samples(self, path, method):
        """Get operation code samples"""
        action = {
            'GET': 'list',
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'partial_update',
            'DELETE': 'destroy',
        }.get(method, None)

        if action == 'list' and '{id}' in path:
            action = 'retrieve'

        if action not in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']:
            return []

        return [
            {
                "lang": "Python",
                "source": render_to_string(f'trionyx/api/codesamples/python/{action}.py.tmpl', {
                    'path': path,
                }) + ''
            },
            {
                "lang": "Javascript",
                "source": render_to_string(f'trionyx/api/codesamples/js/{action}.js', {
                    'path': path,
                }) + ''
            },
        ]


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
            serializer = serializer if serializer else self.generate_model_serializer(model, config)

            if [name for name, field in serializer().get_fields().items() if not field.read_only]:
                base_classes = (ModelViewSet,)
            else:
                base_classes = (
                    mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin, GenericViewSet
                )

            DynamicViewSet = type(
                classname,
                base_classes,
                {}
            )
            DynamicViewSet.model = model
            DynamicViewSet.queryset = model.objects.get_queryset()
            DynamicViewSet.serializer_class = serializer
            DynamicViewSet.permission_classes = (ExtendedDjangoModelPermissions,)
            DynamicViewSet.ordering = ['pk']
            DynamicViewSet.schema = APIAutoSchema(tags=[config.get_verbose_name_plural()])

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
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
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
