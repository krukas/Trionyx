from django.conf import settings
from django.conf.urls import url, include
import django.views.static

urlpatterns = [
    url(r'^', include('trionyx.core.urls', namespace='trionyx')),
]

if settings.DEBUG:
	urlpatterns += [
		url(r'^media/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.MEDIA_ROOT}),
	]