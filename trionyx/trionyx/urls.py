"""
trionyx.trionyx.url
~~~~~~~~~~~~~~~~~~~

:copyright: 2018 by Maikel Martens
:license: GPLv3
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from trionyx import views as core_views
from trionyx.trionyx import views
from trionyx.api.routers import AutoRouter

app_name = 'trionyx'

urlpatterns = [
    path('api/', include(AutoRouter().urls)),

    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('basic-auth/<str:user_type>/', views.basic_auth, name='basic-auth'),

    path('account/edit/', views.UpdateUserAccountView.as_view(), name='edit-account'),
    path('account/view/', views.ViewUserAccountView.as_view(), name='view-account'),

    # Global search
    path('global-search/', views.GlobalSearchJsendView.as_view(), name='global-search'),

    # Tasks
    path('user-tasks/', views.UserTasksJsend.as_view(), name='user-tasks'),

    # Changelog
    path('changelog/', views.ChangelogDialog.as_view(), name='changelog'),

    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/save/', views.SaveDashboardJsendView.as_view(), name='dashboard-save'),
    path('dashboard/widget-data/', views.WidgetDataJsendView.as_view(), name='dashboard-widget-data'),
    path('dashboard/widget-config/<str:code>/', views.WidgetConfigDialog.as_view(), name='dashboard-widget-config'),

    path('model-filter-fields/', views.FilterFieldsJsendView.as_view(), name='model-filter-fields'),

    # Generic model views
    path('model/<str:app>/<str:model>/', core_views.ListView.as_view(), name='model-list'),
    path('model/<str:app>/<str:model>/ajax/', core_views.ListJsendView.as_view(), name='model-list-ajax'),
    path('model/<str:app>/<str:model>/download/', core_views.ListExportView.as_view(), name='model-list-download'),
    path('model/<str:app>/<str:model>/choices/', core_views.ListChoicesJsendView.as_view(), name='model-list-choices'),

    path('model/<str:app>/<str:model>/create/', core_views.CreateView.as_view(), name='model-create'),
    path('model/<str:app>/<str:model>/create/<str:code>/', core_views.CreateView.as_view(), name='model-create-custom'),
    path('model/<str:app>/<str:model>/<int:pk>/', core_views.DetailTabView.as_view(), name='model-view'),
    path('model/<str:app>/<str:model>/<int:pk>/tab/', core_views.DetailTabJsendView.as_view(), name='model-tab'),
    path('model/<str:app>/<str:model>/<int:pk>/layout/<str:code>/', core_views.LayoutView.as_view(), name='model-view-custom'),
    path(
        'model/<str:app>/<str:model>/<int:pk>/layout-update/<str:code>/',
        core_views.LayoutUpdateView.as_view(),
        name='model-layout-update'
    ),

    path('model/<str:app>/<str:model>/<int:pk>/edit/', core_views.UpdateView.as_view(), name='model-edit'),
    path('model/<str:app>/<str:model>/<int:pk>/edit/<str:code>/', core_views.UpdateView.as_view(), name='model-edit-custom'),
    path('model/<str:app>/<str:model>/<int:pk>/delete/', core_views.DeleteView.as_view(), name='model-delete'),

    # Generic Dialog views
    path('dialog/model/<str:app>/<str:model>/<int:pk>/layout/<str:code>/', core_views.LayoutDialog.as_view(), name='model-dialog-view'),
    path('dialog/model/<str:app>/<str:model>/create/', core_views.CreateDialog.as_view(), name='model-dialog-create'),
    path('dialog/model/<str:app>/<str:model>/create/<str:code>/', core_views.CreateDialog.as_view(), name='model-dialog-create-custom'),
    path('dialog/model/<str:app>/<str:model>/<int:pk>/edit/', core_views.UpdateDialog.as_view(), name='model-dialog-edit'),
    path(
        'dialog/model/<str:app>/<str:model>/<int:pk>/edit/<str:code>/', core_views.UpdateDialog.as_view(),
        name='model-dialog-edit-custom'
    ),
    path('dialog/model/<str:app>/<str:model>/<int:pk>/delete/', core_views.DeleteDialog.as_view(), name='model-dialog-delete'),

    # Ajax choices
    path('form/choices/<str:id>/', views.ajaxFormModelChoices, name='form-choices'),

    # Sidebar
    path('sidebar/model/<str:app>/<str:model>/<int:pk>/<str:code>/', views.SidebarJsend.as_view(), name='model-sidebar'),

    # Mass actions
    path('mass/<str:app>/<str:model>/delete/', views.MassDeleteDialog.as_view(), name='model-mass-delete'),
    path('mass/<str:app>/<str:model>/update/', views.MassUpdateView.as_view(), name='model-mass-update'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
else:
    from trionyx.trionyx.views import media_nginx_accel
    urlpatterns += [
        path('media/<path:path>', media_nginx_accel),
    ]
