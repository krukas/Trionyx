from django.conf.urls import url

from trionyx.core import views

urlpatterns = [
    url(r'^login/$', views.LoginView.as_view(), name='login'),
	url(r'^logout/$', views.logout, name='logout'),

    url(r'^account/edit$', views.UpdateUserAccountView.as_view(), name='edit-account'),
]