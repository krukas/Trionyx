"""
trionyx.trionyx.api.serializers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2019 by Maikel Martens
:license: GPLv3
"""
import inspect
from rest_framework.serializers import *  # noqa F403

from trionyx.config import models_config


class SerializerRegister:
    """SerializerRegister class"""

    def __init__(self):
        """Init class"""
        self.serializers = {}

    def register(self, serializer):
        """Add form to register"""
        model_name = self.get_model_alias(serializer.Meta.model)

        if model_name in self.serializers:
            raise Exception("Serializer {} already registered for model {}".format(serializer, model_name))

        self.serializers[model_name] = serializer
        return serializer

    def get_model_alias(self, model_alias):
        """Get model alias if class then convert to alias string"""
        from trionyx.models import BaseModel
        if inspect.isclass(model_alias) and issubclass(model_alias, BaseModel):
            config = models_config.get_config(model_alias)
            return '{}.{}'.format(config.app_label, config.model_name)
        return model_alias

    def get(self, model_alias):
        """Get serializer based on model or model alias"""
        return self.serializers.get(self.get_model_alias(model_alias))


serializer_register = SerializerRegister()
register = serializer_register.register
