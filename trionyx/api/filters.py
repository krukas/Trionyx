"""
trionyx.api.filters
~~~~~~~~~~~~~~~~~~~

:copyright: 2019 by Maikel Martens
:license: GPLv3
"""
import logging

from django.utils.encoding import force_str
from django.core.exceptions import ValidationError
from rest_framework.compat import coreapi, coreschema
from rest_framework.filters import BaseFilterBackend
from rest_framework.exceptions import ValidationError as APIValidationError, APIException
from watson import search as watson

from trionyx.config import models_config
from trionyx.models import filter_queryset_with_user_filters

logger = logging.getLogger(__name__)


class SearchFilter(BaseFilterBackend):
    """Search filter that uses watson search"""

    search_param = '_search'

    search_title = 'Search'
    search_description = 'A search term.'

    def get_search_term(self, request):
        """
        Search terms are set by a ?search=... query parameter,
        and may be comma and/or whitespace delimited.
        """
        params = request.query_params.get(self.search_param, '')
        return params.replace('\x00', '')  # strip null characters

    def filter_queryset(self, request, queryset, view):
        """Filter queryset"""
        if not self.get_search_term(request):
            return queryset
        return watson.filter(queryset, self.get_search_term(request), ranking=False)

    def get_schema_fields(self, view):
        """Get filter schema fields"""
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        return [
            coreapi.Field(
                name=self.search_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_str(self.search_title),
                    description=force_str(self.search_description)
                )
            )
        ]

    def get_schema_operation_parameters(self, view):
        """Get schema operation parameters"""
        return [
            {
                'name': self.search_param,
                'required': False,
                'in': 'query',
                'description': force_str(self.search_description),
                'schema': {
                    'type': 'string',
                },
            },
        ]


class QueryFilter(BaseFilterBackend):
    """Query filter"""

    def filter_queryset(self, request, queryset, view):
        """Filter queryset with filter_queryset_with_user_filters"""
        config = models_config.get_config(queryset.model)

        field_indexed = {
            name: {
                'name': name,
                'label': field['label'],
                'type': field['type'],
                'choices': field['choices'],
            }
            for name, field in config.get_list_fields().items()
        }

        operator_mapping = {
            'isnull': 'null',
            'not': '!=',
            'lt': '<',
            'lte': '<=',
            'gt': '>',
            'gte': '>=',
        }

        errors = []
        filters = []
        for key in request.GET:
            if key.startswith('_'):
                continue

            field, *operator = key.split('__')
            if field not in field_indexed:
                errors.append(f'Invalid field: {field}')
                continue

            if operator and operator[0] not in operator_mapping:
                errors.append(f'Invalid operator: {operator[0]}')
                continue

            filters.append({
                'field': field,
                'operator': operator_mapping.get(operator[0]) if operator else '==',
                'value': request.GET.get(key),
            })

        if errors:
            raise APIValidationError(errors)

        try:
            return filter_queryset_with_user_filters(queryset, filters, raise_exception=True)
        except ValidationError as e:
            raise APIValidationError(e.messages)
        except ValueError as e:
            raise APIValidationError(e)
        except Exception as e:
            logger.exception(e)
            raise APIException()
