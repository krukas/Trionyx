from django.conf.urls import url

from trionyx.core import views

urlpatterns = [
    url(r'^login/$', views.accounts.LoginView.as_view(), name='login'),
	url(r'^logout/$', views.accounts.logout, name='logout'),

    url(r'^account/edit$', views.accounts.UpdateUserAccountView.as_view(), name='edit-account'),
    url(r'^account/view$', views.accounts.ViewUserAccountView.as_view(), name='view-account'),

    # Generic views
    url(r'^model/(?P<app>[\w]+)/(?P<model>[\w]+)/(?P<pk>[0-9]+)/tab/$', views.DetailTabJsendView.as_view(), name='model-tab'),
]