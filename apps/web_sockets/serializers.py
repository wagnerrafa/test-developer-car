"""
Serializers MCP (Model Context Protocol) para comunicação WebSocket.

Este módulo define os serializers utilizados para comunicação MCP via WebSocket,
usando apenas padrões do Django REST Framework.
"""

from datetime import datetime

from rest_framework import serializers


class MCPRequestSerializer(serializers.Serializer):
    """Serializer para requisições MCP."""

    action = serializers.CharField(max_length=100, required=False)
    request_id = serializers.CharField(required=False, allow_null=True)
    data = serializers.DictField(required=False, allow_null=True, default=dict)

    def validate(self, data):
        """Validação customizada para processar dados aninhados."""
        # Se os dados vêm aninhados em 'data', extrair para o nível principal
        if "data" in data and isinstance(data["data"], dict):
            nested_data = data["data"]

            # Extrair campos do nível 'data' se existirem
            for key, value in nested_data.items():
                if key in self.fields:
                    data[key] = value

        return super().validate(data)


class MCPResponseSerializer(serializers.Serializer):
    """Serializer para respostas MCP."""

    success = serializers.BooleanField()
    request_id = serializers.CharField(required=False, allow_null=True)
    data = serializers.DictField(required=False, allow_null=True, default=dict)
    error = serializers.CharField(required=False, allow_null=True)
    timestamp = serializers.CharField(default=datetime.now().isoformat)


class MCPErrorResponseSerializer(MCPResponseSerializer):
    """Serializer para respostas de erro MCP."""

    success = serializers.BooleanField(default=False)
    error_code = serializers.CharField(required=False, allow_null=True)


class CarFilterSerializer(serializers.Serializer):
    """Serializer para filtros de busca de carros."""

    # Filtros de ID
    brand_id = serializers.UUIDField(required=False, allow_null=True)
    brand_name = serializers.CharField(required=False, allow_null=True)
    color_id = serializers.UUIDField(required=False, allow_null=True)
    color_name = serializers.CharField(required=False, allow_null=True)
    engine_id = serializers.UUIDField(required=False, allow_null=True)
    engine_name = serializers.CharField(required=False, allow_null=True)
    car_model_id = serializers.UUIDField(required=False, allow_null=True)
    car_model_name = serializers.CharField(required=False, allow_null=True)
    car_name_id = serializers.UUIDField(required=False, allow_null=True)
    car_name = serializers.CharField(required=False, allow_null=True)

    # Filtros numéricos
    year_manufacture_min = serializers.IntegerField(required=False, allow_null=True, min_value=1900, max_value=9999)
    year_manufacture_max = serializers.IntegerField(required=False, allow_null=True, min_value=1900, max_value=9999)
    year_model_min = serializers.IntegerField(required=False, allow_null=True, min_value=1900, max_value=9999)
    year_model_max = serializers.IntegerField(required=False, allow_null=True, min_value=1900, max_value=9999)
    price_min = serializers.DecimalField(required=False, allow_null=True, max_digits=10, decimal_places=2)
    price_max = serializers.DecimalField(required=False, allow_null=True, max_digits=10, decimal_places=2)
    mileage_min = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    mileage_max = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    doors_min = serializers.IntegerField(required=False, allow_null=True, min_value=2, max_value=8)
    doors_max = serializers.IntegerField(required=False, allow_null=True, min_value=2, max_value=8)

    # Filtros de string
    fuel_type = serializers.CharField(required=False, allow_null=True)
    transmission = serializers.CharField(required=False, allow_null=True)

    # Busca textual
    search = serializers.CharField(required=False, allow_null=True)


class PaginationSerializer(serializers.Serializer):
    """Serializer para configuração de paginação."""

    page = serializers.IntegerField(default=1, min_value=1)
    page_size = serializers.IntegerField(default=20, min_value=1, max_value=100)
    ordering = serializers.CharField(required=False, allow_null=True)


class SearchCarsRequestSerializer(serializers.Serializer):
    """Serializer para requisição de busca de carros."""

    action = serializers.CharField(default="search_cars")
    request_id = serializers.CharField(required=False, allow_null=True)

    # Campos de filtros (diretos)
    brand_id = serializers.UUIDField(required=False, allow_null=True)
    brand_name = serializers.CharField(max_length=255, required=False, allow_null=True)
    color_id = serializers.UUIDField(required=False, allow_null=True)
    color_name = serializers.CharField(max_length=255, required=False, allow_null=True)
    engine_id = serializers.UUIDField(required=False, allow_null=True)
    engine_name = serializers.CharField(max_length=255, required=False, allow_null=True)
    car_model_id = serializers.UUIDField(required=False, allow_null=True)
    car_model_name = serializers.CharField(max_length=255, required=False, allow_null=True)
    car_name_id = serializers.UUIDField(required=False, allow_null=True)
    car_name = serializers.CharField(max_length=255, required=False, allow_null=True)

    # Filtros numéricos
    year_manufacture_min = serializers.IntegerField(required=False, allow_null=True, min_value=1900, max_value=9999)
    year_manufacture_max = serializers.IntegerField(required=False, allow_null=True, min_value=1900, max_value=9999)
    year_model_min = serializers.IntegerField(required=False, allow_null=True, min_value=1900, max_value=9999)
    year_model_max = serializers.IntegerField(required=False, allow_null=True, min_value=1900, max_value=9999)
    price_min = serializers.DecimalField(required=False, allow_null=True, max_digits=10, decimal_places=2)
    price_max = serializers.DecimalField(required=False, allow_null=True, max_digits=10, decimal_places=2)
    mileage_min = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    mileage_max = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    doors_min = serializers.IntegerField(required=False, allow_null=True, min_value=2, max_value=8)
    doors_max = serializers.IntegerField(required=False, allow_null=True, min_value=2, max_value=8)

    # Filtros de string
    fuel_type = serializers.CharField(required=False, allow_null=True)
    transmission = serializers.CharField(required=False, allow_null=True)

    # Busca textual
    search = serializers.CharField(required=False, allow_null=True)

    # Campos de paginação (diretos)
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100)
    ordering = serializers.CharField(required=False, allow_null=True)
    filters = CarFilterSerializer(required=False)
    pagination = PaginationSerializer(required=False)

    def validate(self, data):
        """Validação customizada para processar dados aninhados."""
        nested_data = data
        # Se os dados vêm aninhados em 'data', extrair para o nível principal
        if "data" in data and isinstance(data["data"], dict):
            nested_data = data["data"]

        # Se há filters aninhados, extrair para o nível principal
        if "filters" in nested_data and isinstance(nested_data["filters"], dict):
            filters = nested_data["filters"]
            for key, value in filters.items():
                if key in self.fields:
                    data[key] = value

        # Se há pagination aninhada, extrair para o nível principal
        if "pagination" in nested_data and isinstance(nested_data["pagination"], dict):
            pagination = nested_data["pagination"]
            for key, value in pagination.items():
                if key in self.fields:
                    data[key] = value

        # Extrair outros campos do nível 'data' se existirem
        for key, value in nested_data.items():
            if key in self.fields and key not in ["filters", "pagination"]:
                data[key] = value

        # Aplicar valores padrão se não foram fornecidos
        if "page" not in data or data["page"] is None:
            data["page"] = 1
        if "page_size" not in data or data["page_size"] is None:
            data["page_size"] = 20

        return super().validate(data)


class GetBrandsRequestSerializer(MCPRequestSerializer):
    """Serializer para requisição de marcas."""

    action = serializers.CharField(default="get_brands")


class GetColorsRequestSerializer(MCPRequestSerializer):
    """Serializer para requisição de cores."""

    action = serializers.CharField(default="get_colors")


class GetEnginesRequestSerializer(MCPRequestSerializer):
    """Serializer para requisição de motores."""

    action = serializers.CharField(default="get_engines")


class GetCarDetailsRequestSerializer(MCPRequestSerializer):
    """Serializer para requisição de detalhes do carro."""

    action = serializers.CharField(default="get_car_details")
    car_id = serializers.UUIDField()


class GetFiltersOptionsRequestSerializer(MCPRequestSerializer):
    """Serializer para requisição de opções de filtros."""

    action = serializers.CharField(default="get_filters_options")
