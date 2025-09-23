"""
Example_Config URL Configuration.

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
    1. Import the include function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

"""

from django.conf.urls.static import static
from django.shortcuts import render
from django.urls import include, path

from config.settings import MEDIA_ROOT, MEDIA_URL
from drf_base_config import urls as base_urls
from drf_base_config.settings import APP_NAME, BASE_API_URL, BASE_URL, CURRENT_VERSION


def mcp_demo_view(request):
    """View para demonstração MCP com contexto."""
    websocket_url = f"ws://{request.get_host()}/{APP_NAME}/ws/V1/mcp/cars/"

    context = {"app_name": APP_NAME, "current_version": CURRENT_VERSION, "websocket_url": websocket_url}

    return render(request, "mcp_car_search.html", context)


urlpatterns = [
    path("", include(base_urls)),
    path(f"{BASE_API_URL}cars/", include("apps.cars.urls")),
    path(f"{BASE_URL}mcp-demo/", mcp_demo_view, name="mcp_demo"),
]

urlpatterns += static("/" + MEDIA_URL, document_root=MEDIA_ROOT)
