"""
trionyx.views.ajax
~~~~~~~~~~~~~~~~~~

:copyright: 2019 by Maikel Martens
:license: GPLv3
"""
import logging
from typing import ClassVar, Any

from django.http import JsonResponse
from django.http.request import HttpRequest
from django.views.generic import View

logger = logging.getLogger(__name__)


class JsendView(View):
    """Django view for sending JSON response by the JSend specification

    Specification website: http://labs.omniti.com/labs/jsend
    """

    SUCCESS: ClassVar[str] = 'success'
    ERROR: ClassVar[str] = 'error'
    FAIL: ClassVar[str] = 'fail'
    allow_cors: bool = False

    def __init__(self, *args, **kwargs):
        """Init JsendView"""
        super(JsendView, self).__init__(*args, **kwargs)
        self.status: str = self.SUCCESS
        self.data: Any = ""
        self.message: str = ""

    def handle_request(self, request: HttpRequest, *args, **kwargs):
        """Overide this in your class for handling the request"""
        pass

    def _handle_request(self, request: HttpRequest, *args, **kwargs):
        """Handle request"""
        try:
            data = self.handle_request(request, *args, **kwargs)
        except Exception as e:
            logger.exception(e)
            self.status = self.ERROR
            self.message = str(e)

        if self.status == self.ERROR:
            jsend = {
                'status': self.status,
                'message': self.message
            }
        else:
            jsend = {
                'status': self.status,
                'data': data
            }
        response = JsonResponse(jsend)
        if self.allow_cors:
            response['Access-Control-Allow-Origin'] = "*"
        return response

    def get(self, request: HttpRequest, *args, **kwargs):
        """Handle GET request"""
        return self._handle_request(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs):
        """Handle POST request"""
        return self._handle_request(request, *args, **kwargs)
