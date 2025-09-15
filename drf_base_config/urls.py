"""
config URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

"""

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.templatetags.static import static
from django.urls import include, path, re_path, reverse_lazy
from django.views.generic import TemplateView
from django.views.static import serve
from rest_framework import permissions
from rest_framework.schemas import get_schema_view

from drf_base_apps.views import HealthLiveApi, HealthReadApi, HealthStartApi
from drf_base_config.schema_generator import CustomSchemaGenerator
from drf_base_config.settings import (
    APP_NAME,
    BASE_API_URL,
    BASE_URL,
    CURRENT_VERSION,
    ENABLE_LOGGING_FILE,
    ENV_DEV,
    LOGIN_URL,
    LOGOUT_URL,
    MEDIA_URL,
    PATHS_BACKEND,
    PUBLIC_SWAGGER,
    STATIC_URL,
)
from drf_base_config.views import CustomTemplateView, frontend_index, home, privacidade, sobre_base_django

permission = permissions.AllowAny if ENV_DEV else permissions.IsAdminUser


def favicon_view(request):
    """Redirect to the favicon file."""
    return redirect(f"{settings.STATIC_URL}favicon.ico", permanent=True)


def get_static_swagger():
    """Get the static swagger file URL or fallback to schema API."""
    try:
        return static("swagger.json")
    except ValueError:
        return reverse_lazy("schema-api")


urlpatterns = [
    # Django
    # CORE
    path(LOGIN_URL, LoginView.as_view(template_name="admin/login.html"), name="login"),
    path(LOGOUT_URL, LogoutView.as_view(), name="logout"),
    path(BASE_API_URL, include("drf_base_apps.core.drf_base_user.urls")),
    path("healthz/livez/", HealthLiveApi.as_view(), name="health-check-livez"),
    path("healthz/readyz/", HealthReadApi.as_view(), name="health-check-readyz"),
    path("healthz/startupz/", HealthStartApi.as_view(), name="health-check-startupz"),
    re_path(
        r"^favicon\.ico$",
        lambda _: redirect(f"{settings.STATIC_URL}base_django_static/icon/favicon.ico", permanent=True),
    ),
    re_path(r"^((?!{}|{}).)*$".format(BASE_API_URL, "|".join(PATHS_BACKEND)), frontend_index, name="frontend"),
    re_path(rf"^{MEDIA_URL}(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(rf"^{STATIC_URL}(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
]

urls_docs = [
    # Documentation
    path(
        f"{BASE_API_URL}docs/redoc/",
        get_schema_view(
            title=f"{APP_NAME.title()} Project",
            generator_class=CustomSchemaGenerator,
            description=f"{APP_NAME.title()} Project description",
            version=CURRENT_VERSION,
            permission_classes=[permission],
            public=PUBLIC_SWAGGER,
        ),
        name="schema-api",
    ),
    path(
        f"{BASE_API_URL}docs/redoc/save/",
        get_schema_view(
            title=f"{APP_NAME.title()} Project",
            generator_class=lambda *args, **kwargs: CustomSchemaGenerator(save_swagger=True),
            description=f"{APP_NAME.title()} Project description",
            version=CURRENT_VERSION,
            permission_classes=[permission],
            public=PUBLIC_SWAGGER,
        ),
        name="schema-api-save",
    ),
    path(
        f"{BASE_API_URL}docs/swagger/",
        TemplateView.as_view(
            template_name="api_docs.html",
            extra_context={
                "schema_url": reverse_lazy("schema-api"),
                "current_version": CURRENT_VERSION,
                "app_name": APP_NAME.title(),
            },
        ),
        name=APP_NAME,
    ),
    path(
        f"{BASE_API_URL}docs/swagger/cache/",
        CustomTemplateView.as_view(
            template_name="api_docs.html",
            extra_context={
                "schema_url": get_static_swagger(),
                "current_version": CURRENT_VERSION,
                "app_name": APP_NAME.title(),
            },
        ),
        name="schema-swagger-cache",
    ),
    path(
        f"{BASE_API_URL}docs/swagger/save/",
        CustomTemplateView.as_view(
            template_name="api_docs.html",
            extra_context={
                "schema_url": reverse_lazy("schema-api-save"),
                "current_version": CURRENT_VERSION,
                "app_name": APP_NAME.title(),
            },
        ),
        name="schema-swagger-save",
    ),
]

if ENV_DEV:
    urlpatterns += urls_docs

if ENABLE_LOGGING_FILE:
    urlpatterns.append(path(f"{BASE_URL}logs_admin/", include("drf_base_apps.custom_log_viewer.urls")))

# Páginas estáticas
urlpatterns.append(path(f"{BASE_URL}sobre/", sobre_base_django, name="sobre_base_django"))
urlpatterns.append(path(f"{BASE_URL}privacidade/", privacidade, name="privacidade"))
urlpatterns.append(path(f"{BASE_URL}home/", home, name="home"))
urlpatterns.append(path(f"{APP_NAME}/", home, name="default-home"))
urlpatterns.append(path(f"{BASE_URL}admin/", admin.site.urls, name="admin"))
