"""
URL configuration for the cars app.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/

Examples:
    Function views
        1. Add an import:  from car import views
        2. Add a URL to urlpatterns:  path('', views.CarApi, name='car')
    Class-based views
        1. Add an import:  from car import Car
        2. Add a URL to urlpatterns:  path('', CarApi.as_view(), name='car')
    Including another URLconf
        1. Import the include() function: from django.urls import include, path
        2. Add a URL to urlpatterns:  path('car/', include('car.another_app.urls'))

"""

from django.urls import path

from .views import (
    BrandApi,
    BrandDetailApi,
    CarApi,
    CarDetailApi,
    CarModelApi,
    CarModelDetailApi,
    CarNameApi,
    CarNameDetailApi,
    ColorApi,
    ColorDetailApi,
    EngineApi,
    EngineDetailApi,
)

urlpatterns = [
    path("", CarApi.as_view(), name="car-list-create"),
    path("<uuid:id>/", CarDetailApi.as_view(), name="car-detail-put"),
    path("brand/", BrandApi.as_view(), name="brand-list-create"),
    path("brand/<uuid:id>/", BrandDetailApi.as_view(), name="brand-detail-put"),
    path("color/", ColorApi.as_view(), name="color-list-create"),
    path("color/<uuid:id>/", ColorDetailApi.as_view(), name="color-detail-put"),
    path("engine/", EngineApi.as_view(), name="engine-list-create"),
    path("engine/<uuid:id>/", EngineDetailApi.as_view(), name="engine-detail-put"),
    path("car-name/", CarNameApi.as_view(), name="car-name-list-create"),
    path("car-name/<uuid:id>/", CarNameDetailApi.as_view(), name="car-name-detail-put"),
    path("car-model/", CarModelApi.as_view(), name="car-model-list-create"),
    path("car-model/<uuid:id>/", CarModelDetailApi.as_view(), name="car-model-detail-put"),
]
