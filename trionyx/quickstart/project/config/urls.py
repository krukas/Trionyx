"""Base Project urls"""
from django.conf.urls import url, include

from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token
from trionyx.routers import AutoRouter


urlpatterns = [
    url(r'', include(AutoRouter().urls)),

    # auth API calls
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
    url(r'^api-token-verify/', verify_jwt_token),
]
