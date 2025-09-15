"""URL patterns for user management."""

from django.urls import path

from drf_base_apps.core.drf_base_user.views import UserApi

urlpatterns = [
    path("user/", UserApi.as_view(), name="user-detail"),
]
