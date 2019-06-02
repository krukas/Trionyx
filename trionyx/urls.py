"""
trionyx.urls
~~~~~~~~~~~~

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
import inspect
from django.conf import settings
from django.apps import apps
from django.conf.urls import include
from django.conf.urls.static import static
from django.urls import path, reverse, NoReverseMatch


def model_url(model, view_name, code=None):
    """Shortcut function for getting model url"""
    from trionyx.config import models_config
    view_name = 'trionyx:model-{}'.format(view_name)
    config = models_config.get_config(model)
    kwargs = {
        'app': config.app_label,
        'model': config.model_name,
    }
    if code:
        kwargs['code'] = code

    if not inspect.isclass(model) and not isinstance(model, str):
        try:
            kwargs['pk'] = model.pk
            return reverse(view_name, kwargs=kwargs)
        except NoReverseMatch:
            kwargs.pop('pk')
    return reverse(view_name, kwargs=kwargs)


urlpatterns = [
    path('', include('trionyx.trionyx.urls', namespace='trionyx')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )

if settings.DEBUG and apps.is_installed("debug_toolbar"):
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
