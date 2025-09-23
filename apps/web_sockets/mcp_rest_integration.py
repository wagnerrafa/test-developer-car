"""
Integração MCP com API REST existente.

Este módulo fornece utilitários para integrar o protocolo MCP WebSocket
com as APIs REST existentes, mantendo compatibilidade e reutilizando
validações e permissões.
"""

import logging
from typing import Any, Optional
from uuid import UUID

from django.test import RequestFactory
from rest_framework.request import Request

from apps.cars.views import (
    BrandApi,
    CarApi,
    CarDetailApi,
    CarModelApi,
    CarNameApi,
    ColorApi,
    EngineApi,
)
from apps.web_sockets.serializers import (
    CarFilterSerializer,
    PaginationSerializer,
)

logger = logging.getLogger(__name__)


class MCPRestIntegration:
    """
    Classe para integração entre MCP WebSocket e API REST.

    Esta classe permite que os handlers MCP reutilizem as views REST
    existentes, mantendo todas as validações, permissões e lógica de negócio.
    """

    def __init__(self, user=None):
        """Inicializa a integração com o usuário atual."""
        self.user = user
        self.factory = RequestFactory()

    def create_drf_request(self, method: str = "GET", data: dict | None = None, **kwargs) -> Request:
        """Cria uma requisição DRF para integração com as views existentes."""
        request = self.factory.request(**kwargs)
        request.user = self.user
        request.data = data or {}
        return Request(request)

    def search_cars_via_rest(self, filters: CarFilterSerializer, pagination: PaginationSerializer) -> dict[str, Any]:
        """
        Executa busca de carros via API REST existente.

        Args:
            filters: Filtros de busca
            pagination: Configuração de paginação

        Returns:
            Dados da resposta da API REST

        """
        # Construir parâmetros de query
        query_params = self._build_query_params(filters, pagination)

        return self._call_rest_api(CarApi, error_context="busca de carros", query_params=query_params)

    def get_car_details_via_rest(self, car_id: UUID) -> dict[str, Any]:
        """
        Obtém detalhes de um carro via API REST existente.

        Args:
            car_id: ID do carro

        Returns:
            Dados do carro

        """
        return self._call_rest_api(CarDetailApi, error_context="detalhes do carro", kwargs={"id": car_id})

    def _call_rest_api(
        self,
        view_class,
        method_name: str = "get",
        error_context: str = "dados",
        query_params: dict | None = None,
        data: dict | None = None,
        kwargs: dict | None = None,
    ) -> dict[str, Any]:
        """
        Método genérico para chamar APIs REST.

        Args:
            view_class: Classe da view REST
            method_name: Nome do método da view (padrão: 'get')
            error_context: Contexto para mensagens de erro
            query_params: Parâmetros de query para a requisição
            data: Dados para enviar no corpo da requisição
            kwargs: Argumentos adicionais para a view

        Returns:
            Dados da resposta ou erro

        """
        try:
            # Criar requisição para a API REST
            request = self.create_drf_request(method="GET", data=data)

            # Adicionar parâmetros de query se fornecidos
            if query_params:
                request.query_params = query_params

            # Adicionar kwargs se fornecidos
            if kwargs:
                request.kwargs = kwargs

            # Instanciar e chamar a view REST
            view = view_class()
            view.setup(request)

            # Executar a view com kwargs se fornecidos
            if kwargs:
                response = getattr(view, method_name)(request, **kwargs)
            else:
                response = getattr(view, method_name)(request)

            # Converter resposta para dict
            if hasattr(response, "data"):
                return response.data
            else:
                return {"error": "Resposta inválida da API REST"}

        except Exception as e:
            logger.error(f"Erro na integração REST para {error_context}: {e}", exc_info=True)
            return {"error": f"Erro ao obter {error_context}: {e!s}"}

    def get_brands_via_rest(self) -> dict[str, Any]:
        """
        Obtém marcas via API REST existente.

        Returns:
            Lista de marcas

        """
        return self._call_rest_api(BrandApi, error_context="marcas")

    def get_colors_via_rest(self) -> dict[str, Any]:
        """
        Obtém cores via API REST existente.

        Returns:
            Lista de cores

        """
        return self._call_rest_api(ColorApi, error_context="cores")

    def get_engines_via_rest(self) -> dict[str, Any]:
        """
        Obtém motores via API REST existente.

        Returns:
            Lista de motores

        """
        return self._call_rest_api(EngineApi, error_context="motores")

    def get_car_models_via_rest(self) -> dict[str, Any]:
        """
        Obtém modelos de carros via API REST existente.

        Returns:
            Lista de modelos

        """
        return self._call_rest_api(CarModelApi, error_context="modelos")

    def get_car_names_via_rest(self) -> dict[str, Any]:
        """
        Obtém nomes de carros via API REST existente.

        Returns:
            Lista de nomes de carros

        """
        return self._call_rest_api(CarNameApi, error_context="nomes de carros")

    def _build_query_params(self, filters: CarFilterSerializer, pagination: PaginationSerializer) -> dict[str, Any]:
        """
        Constrói parâmetros de query para a API REST baseado nos filtros MCP.

        Args:
            filters: Filtros MCP
            pagination: Paginação MCP

        Returns:
            Parâmetros de query para a API REST

        """
        query_params = {}

        # Mapeamento de filtros de relacionamento
        relationship_filters = {
            "brand_id": ("car_name__brand_id", str),
            "brand_name": ("car_name__brand__name__icontains", str),
            "color_id": ("color_id", str),
            "color_name": ("color__name__icontains", str),
            "engine_id": ("engine_id", str),
            "engine_name": ("engine__name__icontains", str),
            "car_model_id": ("car_model_id", str),
            "car_model_name": ("car_model__name__icontains", str),
            "car_name_id": ("car_name_id", str),
            "car_name": ("car_name__name__icontains", str),
        }

        # Mapeamento de filtros de escolha
        choice_filters = {
            "fuel_type": "fuel_type",
            "transmission": "transmission",
        }

        # Mapeamento de filtros de range (min/max)
        range_filters = {
            "year_manufacture": "year_manufacture",
            "year_model": "year_model",
            "mileage": "mileage",
            "doors": "doors",
            "price": "price",
        }

        # Mapeamento de parâmetros de paginação
        pagination_params = {
            "page": "page",
            "page_size": "page_size",
            "ordering": "ordering",
        }

        # Aplicar filtros de relacionamento
        for filter_attr, (query_key, transform_func) in relationship_filters.items():
            value = getattr(filters, filter_attr, None)
            if value:
                query_params[query_key] = transform_func(value)

        # Aplicar filtros de escolha
        for filter_attr, query_key in choice_filters.items():
            value = getattr(filters, filter_attr, None)
            if value:
                query_params[query_key] = value

        # Aplicar filtros de range (min/max)
        for field_name, db_field in range_filters.items():
            min_value = getattr(filters, f"{field_name}_min", None)
            max_value = getattr(filters, f"{field_name}_max", None)

            if min_value is not None:
                query_params[f"{db_field}__gte"] = min_value
            if max_value is not None:
                query_params[f"{db_field}__lte"] = max_value

        # Aplicar busca textual
        if filters.search:
            query_params["search"] = filters.search

        # Aplicar parâmetros de paginação
        for pagination_attr, query_key in pagination_params.items():
            value = getattr(pagination, pagination_attr, None)
            if value:
                query_params[query_key] = value

        return query_params

    def validate_mcp_request(self, request_data: dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Valida uma requisição MCP usando as validações da API REST.

        Args:
            request_data: Dados da requisição MCP

        Returns:
            Tupla (is_valid, error_message)

        """
        try:
            # Validar estrutura básica
            if "action" not in request_data:
                return False, "Campo 'action' é obrigatório"

            # Validar ação suportada
            supported_actions = [
                "search_cars",
                "get_brands",
                "get_colors",
                "get_engines",
                "get_car_details",
                "get_filters_options",
            ]

            if request_data["action"] not in supported_actions:
                return False, f"Ação '{request_data['action']}' não suportada"

            # Validações específicas por ação
            if request_data["action"] == "search_cars":
                return self._validate_search_cars_request(request_data)
            elif request_data["action"] == "get_car_details":
                return self._validate_get_car_details_request(request_data)

            return True, None

        except Exception as e:
            logger.error(f"Erro na validação MCP: {e}", exc_info=True)
            return False, f"Erro na validação: {e!s}"

    def _validate_search_cars_request(self, request_data: dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Valida requisição de busca de carros."""
        try:
            # Validar filtros se fornecidos
            if "filters" in request_data:
                filters_data = request_data["filters"]
                CarFilterSerializer(data=filters_data)

            # Validar paginação se fornecida
            if "pagination" in request_data:
                pagination_data = request_data["pagination"]
                PaginationSerializer(data=pagination_data)

            return True, None

        except Exception as e:
            return False, f"Erro na validação de filtros: {e!s}"

    def _validate_get_car_details_request(self, request_data: dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Valida requisição de detalhes do carro."""
        try:
            if "car_id" not in request_data:
                return False, "Campo 'car_id' é obrigatório"

            # Validar se é um UUID válido
            UUID(request_data["car_id"])

            return True, None

        except ValueError:
            return False, "car_id deve ser um UUID válido"
        except Exception as e:
            return False, f"Erro na validação: {e!s}"
