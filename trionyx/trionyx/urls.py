"""
trionyx.trionyx.url
~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from django.conf import settings
from django.conf.urls import include, url
import django.views.static

from trionyx.trionyx import views

urlpatterns = [
    url(r'^login/$', views.accounts.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.accounts.logout, name='logout'),

    url(r'^account/edit$', views.accounts.UpdateUserAccountView.as_view(), name='edit-account'),
    url(r'^account/view$', views.accounts.ViewUserAccountView.as_view(), name='view-account'),

    # Generic model views
    url(r'^model/(?P<app>[\w]+)/(?P<model>[\w]+)/$', views.ListView.as_view(), name='model-list'),
    url(r'^model/(?P<app>[\w]+)/(?P<model>[\w]+)/ajax/$', views.ListJsendView.as_view(), name='model-list-ajax'),
    url(r'^model/(?P<app>[\w]+)/(?P<model>[\w]+)/download/$', views.ListExportView.as_view(), name='model-list-download'),

    url(r'^model/(?P<app>[\w]+)/(?P<model>[\w]+)/create/$', views.CreateView.as_view(), name='model-create'),
    url(r'^model/(?P<app>[\w]+)/(?P<model>[\w]+)/(?P<pk>[0-9]+)/$', views.DetailTabView.as_view(), name='model-view'),
    url(r'^model/(?P<app>[\w]+)/(?P<model>[\w]+)/(?P<pk>[0-9]+)/tab/$', views.DetailTabJsendView.as_view(), name='model-tab'),

    url(r'^model/(?P<app>[\w]+)/(?P<model>[\w]+)/(?P<pk>[0-9]+)/edit/$', views.UpdateView.as_view(), name='model-edit'),
    url(r'^model/(?P<app>[\w]+)/(?P<model>[\w]+)/(?P<pk>[0-9]+)/delete/$', views.DeleteView.as_view(), name='model-delete'),

    # Generic Dialog views
    url(r'^dialog/model/(?P<app>[\w]+)/(?P<model>[\w]+)/create/$', views.CreateDialog.as_view(), name='model-dialog-create'),
    url(r'^dialog/model/(?P<app>[\w]+)/(?P<model>[\w]+)/(?P<pk>[0-9]+)/edit/$', views.UpdateDialog.as_view(), name='model-dialog-edit'),

]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.MEDIA_ROOT}),
    ]

    import debug_toolbar

    urlpatterns += [url(r'^__debug__/', include(debug_toolbar.urls))]
else:
    from trionyx.trionyx.views.core import media_nginx_accel
    urlpatterns += [
        url(r'^media\/(?P<path>.*)$', media_nginx_accel),
    ]