"""
trionyx.api.filters
~~~~~~~~~~~~~~~~~~~

:copyright: 2019 by Maikel Martens
:license: GPLv3
"""
from django.utils.encoding import force_str
from rest_framework.compat import coreapi, coreschema
from rest_framework.filters import BaseFilterBackend
from rest_framework.settings import api_settings
from watson import search as watson


class SearchFilter(BaseFilterBackend):
    """Search filter that uses watson search"""

    search_param = api_settings.SEARCH_PARAM

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
