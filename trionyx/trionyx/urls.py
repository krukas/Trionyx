"""
trionyx.trionyx.url
~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from trionyx.trionyx import views

app_name = 'trionyx'

urlpatterns = [
    path('login/', views.accounts.LoginView.as_view(), name='login'),
    path('logout/', views.accounts.logout, name='logout'),

    path('account/edit/', views.accounts.UpdateUserAccountView.as_view(), name='edit-account'),
    path(r'account/view', views.accounts.ViewUserAccountView.as_view(), name='view-account'),

    # Global search
    path('global-search', views.GlobalSearchJsendView.as_view(), name='global-search'),

    # Generic model views
    path('model/<str:app>/<str:model>/', views.ListView.as_view(), name='model-list'),
    path('model/<str:app>/<str:model>/ajax/', views.ListJsendView.as_view(), name='model-list-ajax'),
    path('model/<str:app>/<str:model>/download/', views.ListExportView.as_view(), name='model-list-download'),
    path('model/<str:app>/<str:model>/choices/', views.ListChoicesJsendView.as_view(), name='model-list-choices'),

    path('model/<str:app>/<str:model>/create/', views.CreateView.as_view(), name='model-create'),
    path('model/<str:app>/<str:model>/<int:pk>/', views.DetailTabView.as_view(), name='model-view'),
    path('model/<str:app>/<str:model>/<int:pk>/tab/', views.DetailTabJsendView.as_view(), name='model-tab'),

    path('model/<str:app>/<str:model>/<int:pk>/edit/', views.UpdateView.as_view(), name='model-edit'),
    path('model/<str:app>/<str:model>/<int:pk>/delete/', views.DeleteView.as_view(), name='model-delete'),

    # Generic Dialog views
    path('dialog/model/<str:app>/<str:model>/create/', views.CreateDialog.as_view(), name='model-dialog-create'),
    path('dialog/model/<str:app>/<str:model>/<int:pk>/edit/', views.UpdateDialog.as_view(), name='model-dialog-edit'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
else:
    from trionyx.trionyx.views.core import media_nginx_accel
    urlpatterns += [
        path('media/<path:path>', media_nginx_accel),
    ]
