"""
trionyx.urls
~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.urls import path

urlpatterns = [
    path('', include('trionyx.trionyx.urls', namespace='trionyx')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
