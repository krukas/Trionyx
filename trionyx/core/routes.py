"""
trionyx.core.routes
~~~~~~~~~~~~~~~~~~~

Core api routes

:copyright: 2017 by Maikel Martens
:license: GPLv3
"""
from trionyx.routers import router

from . import api


apiroutes = [
    router('permission/tree', api.PermissionTreeViewSet, 'permission_trees'),

    router('application/config', api.ApplicationConfigViewSet, 'application_config'),
    router('application/menu', api.ApplicationMenuViewSet, 'application_menu'),
    router('application/model/definitions', api.ModelDefinitionsViewSet, 'model_definitions'),
    router('application/model/views', api.ModelViewsViewSet, 'model_views'),
]
