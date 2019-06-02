"""
trionyx.trionyx.search
~~~~~~~~~~~~~~~~~~~~~~

Add search and global search to models

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from watson import search

from trionyx.config import models_config


class ModelSearchAdapter(search.SearchAdapter):
    """Generic search adapter for Trionyx models"""

    def get_title(self, obj):
        """Set search entry title for object"""
        from trionyx.renderer import LazyFieldRenderer
        search_title = self.get_model_config_value(obj, 'search_title')

        if not search_title:
            return super().get_title(obj)

        return search_title.format(**{
            field.name: LazyFieldRenderer(obj, field.name)
            for field in models_config.get_config(obj).get_fields(True, True)
        })

    def get_description(self, obj):
        """Set search entry description for object"""
        from trionyx.renderer import LazyFieldRenderer
        search_description = self.get_model_config_value(obj, 'search_description')

        if not search_description:
            return super().get_description(obj)

        return search_description.format(**{
            field.name: LazyFieldRenderer(obj, field.name)
            for field in models_config.get_config(obj).get_fields(True, True)
        })

    def get_model_config_value(self, obj, name):
        """Get config value for given model"""
        config = models_config.get_config(obj)
        return getattr(config, name)

    def get_url(self, obj):
        """Return the URL of the given obj."""
        return models_config.get_config(obj).get_absolute_url(obj)


def auto_register_search_models():
    """Auto register all search models"""
    for config in models_config.get_all_configs(False):
        if config.disable_search_index:
            continue

        search.register(
            config.model.objects.get_queryset(),
            ModelSearchAdapter,
            fields=config.search_fields,
            exclude=config.search_exclude_fields,
        )
