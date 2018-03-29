from django.conf.urls import url

from trionyx.core import views

urlpatterns = [
    url(r'^login/$', views.accounts.LoginView.as_view(), name='login'),
	url(r'^logout/$', views.accounts.logout, name='logout'),

    url(r'^account/edit$', views.accounts.UpdateUserAccountView.as_view(), name='edit-account'),
    url(r'^account/view$', views.accounts.ViewUserAccountView.as_view(), name='view-account'),

    # Generic model views
    url(r'^model/(?P<app>[\w]+)/(?P<model>[\w]+)/$', views.ListView.as_view(), name='model-list'),
    url(r'^model/(?P<app>[\w]+)/(?P<model>[\w]+)/ajax/$', views.ListJsendView.as_view(), name='model-list-ajax'),
    url(r'^model/(?P<app>[\w]+)/(?P<model>[\w]+)/create/$', views.CreateView.as_view(), name='model-create'),

    url(r'^model/(?P<app>[\w]+)/(?P<model>[\w]+)/(?P<pk>[0-9]+)/$', views.DetailTabView.as_view(), name='model-view'),
    url(r'^model/(?P<app>[\w]+)/(?P<model>[\w]+)/(?P<pk>[0-9]+)/tab/$', views.DetailTabJsendView.as_view(), name='model-tab'),

    url(r'^model/(?P<app>[\w]+)/(?P<model>[\w]+)/(?P<pk>[0-9]+)/edit/$', views.UpdateView.as_view(), name='model-edit'),
    url(r'^model/(?P<app>[\w]+)/(?P<model>[\w]+)/(?P<pk>[0-9]+)/delete/$', views.DeleteView.as_view(), name='model-delete'),
]