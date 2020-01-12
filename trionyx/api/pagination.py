"""
trionyx.trionyx.api.pagination
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2019 by Maikel Martens
:license: GPLv3
"""
from collections import OrderedDict
from rest_framework.response import Response

from rest_framework.pagination import PageNumberPagination as RestPageNumberPagination


class PageNumberPagination(RestPageNumberPagination):
    """Api Pagination class"""

    max_page_size = 1000

    def get_paginated_response(self, data):
        """Get paginated response, added extra fields"""
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('page', self.page.number),
            ('per_page', self.page.paginator.per_page),
            ('num_pages', self.page.paginator.num_pages),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
