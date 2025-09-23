"""
Handlers MCP (Model Context Protocol) para WebSocket.

Este módulo contém os handlers que processam requisições MCP via WebSocket,
integrando com a API REST existente para fornecer funcionalidades de busca
de carros em tempo real.
"""

import logging
from datetime import datetime
from typing import Any

from asgiref.sync import sync_to_async
from django.db.models import Count, Max, Min, Q
from django.test import RequestFactory
from rest_framework import serializers
from rest_framework.request import Request

from apps.cars.models import Brand, Car, Color, Engine
from apps.cars.schemas import CarDetailSchema
from apps.web_sockets.mcp_rest_integration import MCPRestIntegration
from apps.web_sockets.serializers import (
    MCPRequestSerializer,
    SearchCarsRequestSerializer,
)
from drf_base_apps.utils import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


def create_mcp_response(success=True, data=None, error=None, request_id=None):
    """Cria uma resposta MCP padronizada."""
    return {
        "type": "mcp_response",
        "success": success,
        "request_id": request_id,
        "data": data or {},
        "error": error,
        "timestamp": datetime.now().isoformat(),
    }


def create_mcp_error(error_message, error_code="INTERNAL_ERROR", request_id=None):
    """Cria uma resposta de erro MCP padronizada."""
    return {
        "type": "mcp_error",
        "success": False,
        "request_id": request_id,
        "data": {},
        "error": error_message,
        "error_code": error_code,
        "timestamp": datetime.now().isoformat(),
    }


class MCPBrandSerializer(serializers.ModelSerializer):
    """Serializer customizado para marcas com contagem de carros."""

    count = serializers.IntegerField(read_only=True)

    class Meta:
        """Meta class for BrandWithCountSerializer."""

        model = Brand
        fields = ["id", "name", "count"]


class MCPColorSerializer(serializers.ModelSerializer):
    """Serializer customizado para cores com contagem de carros."""

    count = serializers.IntegerField(read_only=True)

    class Meta:
        """Meta class for ColorWithCountSerializer."""

        model = Color
        fields = ["id", "name", "count"]


class MCPEngineSerializer(serializers.ModelSerializer):
    """Serializer customizado para motores com contagem de carros."""

    count = serializers.IntegerField(read_only=True)

    class Meta:
        """Meta class for EngineWithCountSerializer."""

        model = Engine
        fields = ["id", "name", "displacement", "power", "count"]


class MCPHandler:
    """Classe base para handlers MCP."""

    def __init__(self, user=None):
        """Inicializa o handler com o usuário atual."""
        self.user = user
        self.factory = RequestFactory()
        self.rest_integration = MCPRestIntegration(user=user)

    def create_drf_request(self, method: str = "GET", data: dict | None = None, **kwargs) -> Request:
        """Cria uma requisição DRF para integração com as views existentes."""
        request = self.factory.request(**kwargs)
        request.user = self.user
        request.data = data or {}
        return Request(request)

    async def handle_request(self, request_data: dict[str, Any]) -> dict[str, Any]:
        """Processa uma requisição MCP e retorna a resposta apropriada."""
        try:
            # Determinar qual serializer usar baseado na ação
            action = request_data.get("data", {}).get("action")

            if action == "search_cars":
                serializer = SearchCarsRequestSerializer(data=request_data.get("data", {}))
            else:
                serializer = MCPRequestSerializer(data=request_data)

            if not serializer.is_valid():
                logger.error(f"Erro de validação: {serializer.errors}")
                return create_mcp_error(
                    error_message=f"Dados de requisição inválidos: {serializer.errors}",
                    error_code="INVALID_REQUEST",
                    request_id=request_data.get("request_id"),
                )

            validated_data = serializer.validated_data
            request_id = validated_data.get("request_id")

            # Roteamento baseado na ação
            handler_map = {
                "search_cars": self.handle_search_cars,
                "get_brands": self.handle_get_brands,
                "get_colors": self.handle_get_colors,
                "get_engines": self.handle_get_engines,
                "get_car_details": self.handle_get_car_details,
                "get_filters_options": self.handle_get_filters_options,
            }

            handler = handler_map.get(action)
            if not handler:
                return create_mcp_error(
                    error_message=f"Ação '{action}' não suportada",
                    error_code="UNSUPPORTED_ACTION",
                    request_id=request_id,
                )

            return await handler(validated_data)

        except Exception as e:
            logger.error(f"Erro ao processar requisição MCP: {e}", exc_info=True)
            return create_mcp_error(
                error_message=f"Erro interno do servidor: {e!s}",
                error_code="INTERNAL_ERROR",
                request_id=request_data.get("request_id"),
            )


class CarMCPHandler(MCPHandler):
    """Handler específico para operações de carros via MCP."""

    async def handle_search_cars(self, validated_data: dict[str, Any]) -> dict[str, Any]:
        """Handle para busca de carros com filtros."""
        try:
            # Obter dados diretamente do serializer validado
            request_id = validated_data.get("request_id")

            # Extrair filtros e Remover valores None dos filtros
            filters = {k: v for k, v in validated_data.items() if v is not None}

            # Extrair paginação (campos diretos do serializer)
            page = validated_data.get("page", 1)
            page_size = validated_data.get("page_size", 20)
            ordering = validated_data.get("ordering", "-created_at")

            # Construir query
            queryset = Car.objects.select_related("car_name__brand", "car_model", "color", "engine").all()

            # Aplicar filtros
            queryset = await self._apply_filters(queryset, filters)

            # Contar total antes da paginação
            total = await sync_to_async(queryset.count)()

            # Aplicar ordenação
            if ordering:
                queryset = queryset.order_by(ordering)

            # Aplicar paginação
            start = (page - 1) * page_size
            end = start + page_size
            cars = await sync_to_async(list)(queryset[start:end])

            # Serializar resultados usando o serializer do Django
            serializer = CarDetailSchema(cars, many=True)
            car_results = serializer.data

            # Calcular total de páginas
            total_pages = (total + page_size - 1) // page_size

            response_data = {
                "results": car_results,  # Já são dados serializados do Django
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
            }

            return create_mcp_response(success=True, data=response_data, request_id=request_id)

        except Exception as e:
            logger.error(f"Erro na busca de carros: {e}", exc_info=True)
            return create_mcp_error(
                error_message=f"Erro na busca de carros: {e!s}", error_code="SEARCH_ERROR", request_id=request_id
            )

    async def _apply_filters(self, queryset, filters: dict[str, Any]):
        """Aplica filtros à queryset de carros."""
        if not filters:
            return queryset

        # Mapeamento de filtros para campos da queryset
        filter_mappings = {
            # Filtros de relacionamento por ID
            "brand_id": "car_name__brand_id",
            "color_id": "color_id",
            "engine_id": "engine_id",
            "car_model_id": "car_model_id",
            "car_name_id": "car_name_id",
            # Filtros de relacionamento por nome (busca parcial)
            "brand_name": ("car_name__brand__name__icontains",),
            "color_name": ("color__name__icontains",),
            "engine_name": ("engine__name__icontains",),
            "car_model_name": ("car_model__name__icontains",),
            "car_name": ("car_name__name__icontains",),
            # Filtros de escolha
            "fuel_type": "fuel_type",
            "transmission": "transmission",
        }

        # Filtros numéricos com range (min/max)
        range_filters = {
            "year_manufacture": "year_manufacture",
            "year_model": "year_model",
            "mileage": "mileage",
            "doors": "doors",
            "price": "price",
        }

        # Aplicar filtros simples
        for filter_key, field_path in filter_mappings.items():
            if filters.get(filter_key):
                if isinstance(field_path, tuple):
                    # Filtros com lookup personalizado
                    queryset = queryset.filter(**{field_path[0]: filters[filter_key]})
                else:
                    # Filtros diretos
                    queryset = queryset.filter(**{field_path: filters[filter_key]})

        # Aplicar filtros de range (min/max)
        for field_name, db_field in range_filters.items():
            min_key = f"{field_name}_min"
            max_key = f"{field_name}_max"

            if min_key in filters and filters[min_key] is not None:
                queryset = queryset.filter(**{f"{db_field}__gte": filters[min_key]})

            if max_key in filters and filters[max_key] is not None:
                queryset = queryset.filter(**{f"{db_field}__lte": filters[max_key]})

        # Busca textual geral
        if filters.get("search"):
            search_term = filters["search"]
            search_fields = [
                "car_name__name__icontains",
                "car_name__brand__name__icontains",
                "car_model__name__icontains",
                "color__name__icontains",
                "engine__name__icontains",
            ]

            search_q = Q()
            for field in search_fields:
                search_q |= Q(**{field: search_term})

            queryset = queryset.filter(search_q)

        return queryset

    async def handle_get_brands(self, validated_data: dict[str, Any]) -> dict[str, Any]:
        """Handle para obter marcas disponíveis com contagem de carros."""
        try:
            request_id = validated_data.get("request_id")

            # Obter marcas com contagem de carros
            brands_data = await sync_to_async(list)(
                Brand.objects.annotate(count=Count("car_names__cars", distinct=True))
                .filter(count__gt=0)
                .order_by("name")
            )

            # Usar serializer customizado para MCP
            serializer = MCPBrandSerializer(brands_data, many=True)
            brands_serialized = serializer.data

            return create_mcp_response(success=True, data={"brands": brands_serialized}, request_id=request_id)

        except Exception as e:
            logger.error(f"Erro ao obter marcas: {e}", exc_info=True)
            return create_mcp_error(
                error_message=f"Erro ao obter marcas: {e!s}", error_code="BRANDS_ERROR", request_id=request_id
            )

    async def handle_get_colors(self, validated_data: dict[str, Any]) -> dict[str, Any]:
        """Handle para obter cores disponíveis com contagem de carros."""
        try:
            request_id = validated_data.get("request_id")

            # Obter cores com contagem de carros
            colors_data = await sync_to_async(list)(
                Color.objects.annotate(count=Count("cars", distinct=True)).filter(count__gt=0).order_by("name")
            )

            # Usar serializer customizado para MCP
            serializer = MCPColorSerializer(colors_data, many=True)
            colors_serialized = serializer.data

            return create_mcp_response(success=True, data={"colors": colors_serialized}, request_id=request_id)

        except Exception as e:
            logger.error(f"Erro ao obter cores: {e}", exc_info=True)
            return create_mcp_error(
                error_message=f"Erro ao obter cores: {e!s}", error_code="COLORS_ERROR", request_id=request_id
            )

    async def handle_get_engines(self, validated_data: dict[str, Any]) -> dict[str, Any]:
        """Handle para obter motores disponíveis com contagem de carros."""
        try:
            request_id = validated_data.get("request_id")

            # Obter motores com contagem de carros
            engines_data = await sync_to_async(list)(
                Engine.objects.annotate(count=Count("cars", distinct=True)).filter(count__gt=0).order_by("name")
            )

            # Usar serializer customizado para MCP
            serializer = MCPEngineSerializer(engines_data, many=True)
            engines_serialized = serializer.data

            return create_mcp_response(success=True, data={"engines": engines_serialized}, request_id=request_id)

        except Exception as e:
            logger.error(f"Erro ao obter motores: {e}", exc_info=True)
            return create_mcp_error(
                error_message=f"Erro ao obter motores: {e!s}", error_code="ENGINES_ERROR", request_id=request_id
            )

    async def handle_get_car_details(self, validated_data: dict[str, Any]) -> dict[str, Any]:
        """Handle para obter detalhes de um carro específico."""
        try:
            request_id = validated_data.get("request_id")
            car_id = validated_data.get("data", {}).get("car_id")
            if not car_id:
                return create_mcp_error(
                    error_message="ID do carro é obrigatório", error_code="MISSING_CAR_ID", request_id=request_id
                )

            try:
                car = await sync_to_async(
                    Car.objects.select_related("car_name__brand", "car_model", "color", "engine").get
                )(id=car_id)
            except Car.DoesNotExist:
                return create_mcp_error(
                    error_message="Carro não encontrado", error_code="CAR_NOT_FOUND", request_id=request_id
                )

            # Serializar carro usando o serializer do Django
            serializer = CarDetailSchema(car)
            car_data = serializer.data

            return create_mcp_response(
                success=True, data={"car": car_data}, request_id=request_id  # Já são dados serializados do Django
            )

        except Exception as e:
            logger.error(f"Erro ao obter detalhes do carro: {e}", exc_info=True)
            return create_mcp_error(
                error_message=f"Erro ao obter detalhes do carro: {e!s}",
                error_code="CAR_DETAILS_ERROR",
                request_id=request_id,
            )

    async def handle_get_filters_options(self, validated_data: dict[str, Any]) -> dict[str, Any]:
        """Handle para obter opções de filtros disponíveis."""
        try:
            request_id = validated_data.get("request_id")

            # Obter tipos de combustível únicos
            fuel_types = await sync_to_async(list)(
                Car.objects.values_list("fuel_type", flat=True).distinct().order_by("fuel_type")
            )

            # Obter tipos de transmissão únicos
            transmissions = await sync_to_async(list)(
                Car.objects.values_list("transmission", flat=True).distinct().order_by("transmission")
            )

            # Obter faixas de anos
            year_stats = await sync_to_async(Car.objects.aggregate)(
                min_year_manufacture=Min("year_manufacture"),
                max_year_manufacture=Max("year_manufacture"),
                min_year_model=Min("year_model"),
                max_year_model=Max("year_model"),
            )

            # Obter faixas de preço
            price_stats = await sync_to_async(Car.objects.aggregate)(min_price=Min("price"), max_price=Max("price"))

            # Obter faixas de quilometragem
            mileage_stats = await sync_to_async(Car.objects.aggregate)(
                min_mileage=Min("mileage"), max_mileage=Max("mileage")
            )

            # Obter faixas de portas
            doors_stats = await sync_to_async(Car.objects.aggregate)(min_doors=Min("doors"), max_doors=Max("doors"))

            filters_options = {
                "fuel_types": list(fuel_types),
                "transmissions": list(transmissions),
                "year_range": {
                    "min_manufacture": year_stats["min_year_manufacture"] or 1900,
                    "max_manufacture": year_stats["max_year_manufacture"] or 9999,
                    "min_model": year_stats["min_year_model"] or 1900,
                    "max_model": year_stats["max_year_model"] or 9999,
                },
                "price_range": {
                    "min": float(price_stats["min_price"] or 0),
                    "max": float(price_stats["max_price"] or 0),
                },
                "mileage_range": {"min": mileage_stats["min_mileage"] or 0, "max": mileage_stats["max_mileage"] or 0},
                "doors_range": {"min": doors_stats["min_doors"] or 2, "max": doors_stats["max_doors"] or 8},
            }

            return create_mcp_response(success=True, data=filters_options, request_id=request_id)

        except Exception as e:
            logger.error(f"Erro ao obter opções de filtros: {e}", exc_info=True)
            return create_mcp_error(
                error_message=f"Erro ao obter opções de filtros: {e!s}",
                error_code="FILTERS_OPTIONS_ERROR",
                request_id=request_id,
            )
