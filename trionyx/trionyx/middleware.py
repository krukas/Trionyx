"""
trionyx.trionyx.middleware
~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
import threading
from re import compile

from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings
from django.utils import timezone

LOCAL_DATA = threading.local()

EXEMPT_URLS = [
    compile(reverse(settings.LOGIN_URL).lstrip('/')),
]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]


class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to view any page other
    than LOGIN_URL. Exemptions to this requirement can optionally be specified
    in settings via a list of regular expressions in LOGIN_EXEMPT_URLS (which
    you can copy from your urls.py).

    Requires authentication middleware and template context processors to be
    loaded. You'll get an error if they aren't.
    """

    def __init__(self, get_response):
        """Init"""
        self.get_response = get_response

    def __call__(self, request):
        """Check if user is logged in"""
        if not request.user.is_authenticated:
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in EXEMPT_URLS):
                return HttpResponseRedirect(reverse(settings.LOGIN_URL))

        return self.get_response(request)


class GlobalRequestMiddleware:
    """Store request in thread local data"""

    def __init__(self, get_response):
        """Init"""
        self.get_response = get_response

    def __call__(self, request):
        """Store request in local data"""
        LOCAL_DATA.request = request
        try:
            return self.get_response(request)
        finally:
            del LOCAL_DATA.request


class LastLoginMiddleware:
    """Set last login for user"""

    def __init__(self, get_response):
        """Init"""
        self.get_response = get_response

    def __call__(self, request):
        """Set last login"""
        minute_ago = timezone.now() - timezone.timedelta(minutes=1)
        if request.user.is_authenticated and (not request.user.last_online or request.user.last_online <= minute_ago):
            request.user.last_online = timezone.now()
            request.user.save(update_fields=['last_online'])

        return self.get_response(request)
