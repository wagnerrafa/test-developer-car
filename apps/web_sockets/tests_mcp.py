"""
Testes para funcionalidades MCP (Model Context Protocol) WebSocket.

Este módulo contém testes unitários e de integração para as funcionalidades
MCP implementadas, incluindo handlers, schemas e consumer WebSocket.
"""

import json
import uuid

import pytest
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase

from apps.cars.models import Brand, Car, CarModel, CarName, Color, Engine
from apps.web_sockets.mcp_consumer import MCPCarSocket, MCPCarSocketV2
from apps.web_sockets.mcp_handlers import CarMCPHandler
from apps.web_sockets.mcp_rest_integration import MCPRestIntegration
from apps.web_sockets.serializers import (
    CarFilterSerializer,
    MCPRequestSerializer,
    PaginationSerializer,
)

User = get_user_model()


class MCPSchemasTestCase(TestCase):
    """Testes para schemas MCP."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

    def test_car_filter_schema_validation(self):
        """Testa validação do schema de filtros de carros."""
        # Teste com filtros válidos
        valid_filters = {
            "brand_name": "Toyota",
            "year_manufacture_min": 2020,
            "year_manufacture_max": 2023,
            "price_min": 50000.0,
            "price_max": 100000.0,
        }

        filter_schema = CarFilterSerializer(data=valid_filters)
        self.assertEqual(filter_schema.brand_name, "Toyota")
        self.assertEqual(filter_schema.year_manufacture_min, 2020)
        self.assertEqual(filter_schema.year_manufacture_max, 2023)

    def test_car_filter_schema_invalid_ranges(self):
        """Testa validação de faixas inválidas no schema de filtros."""
        # Teste com faixa de ano inválida
        invalid_filters = {"year_manufacture_min": 2023, "year_manufacture_max": 2020}  # Max menor que min

        with self.assertRaises(ValueError):
            CarFilterSerializer(data=invalid_filters)

    def test_pagination_schema_validation(self):
        """Testa validação do schema de paginação."""
        # Teste com paginação válida
        valid_pagination = {"page": 1, "page_size": 20, "ordering": "-created_at"}

        pagination_schema = PaginationSerializer(data=valid_pagination)
        self.assertEqual(pagination_schema.page, 1)
        self.assertEqual(pagination_schema.page_size, 20)
        self.assertEqual(pagination_schema.ordering, "-created_at")

    def test_mcp_request_schema(self):
        """Testa validação do schema de requisição MCP."""
        valid_request = {
            "action": "search_cars",
            "request_id": "test_123",
            "data": {"filters": {"brand_name": "Honda"}},
        }

        request_schema = MCPRequestSerializer(data=valid_request)
        self.assertEqual(request_schema.action, "search_cars")
        self.assertEqual(request_schema.request_id, "test_123")


class MCPHandlersTestCase(TestCase):
    """Testes para handlers MCP."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        # Criar dados de teste
        self.brand = Brand.objects.create(name="Toyota")
        self.color = Color.objects.create(name="Branco")
        self.engine = Engine.objects.create(name="1.6 Flex", displacement="1.6", power=120)
        self.car_model = CarModel.objects.create(name="Sedan")
        self.car_name = CarName.objects.create(name="Corolla", brand=self.brand)

        self.car = Car.objects.create(
            car_name=self.car_name,
            car_model=self.car_model,
            year_manufacture=2023,
            year_model=2024,
            engine=self.engine,
            fuel_type="flex",
            color=self.color,
            mileage=15000,
            doors=4,
            transmission="automatic",
            price=120000.0,
        )

        self.handler = CarMCPHandler(user=self.user)

    def test_handle_search_cars_with_filters(self):
        """Testa busca de carros com filtros."""
        request_data = {
            "action": "search_cars",
            "request_id": "test_123",
            "filters": {"brand_name": "Toyota"},
            "pagination": {"page": 1, "page_size": 10},
        }

        response = self.handler.handle_request(request_data)

        self.assertTrue(response.success)
        self.assertIsNotNone(response.data)
        self.assertIn("results", response.data)
        self.assertIn("total", response.data)
        self.assertEqual(response.data["total"], 1)

    def test_handle_search_cars_no_results(self):
        """Testa busca de carros sem resultados."""
        request_data = {
            "action": "search_cars",
            "request_id": "test_123",
            "filters": {"brand_name": "Ferrari"},  # Marca que não existe
        }

        response = self.handler.handle_request(request_data)

        self.assertTrue(response.success)
        self.assertEqual(response.data["total"], 0)
        self.assertEqual(len(response.data["results"]), 0)

    def test_handle_get_brands(self):
        """Testa obtenção de marcas."""
        request_data = {"action": "get_brands", "request_id": "test_123"}

        response = self.handler.handle_request(request_data)

        self.assertTrue(response.success)
        self.assertIn("brands", response.data)
        self.assertEqual(len(response.data["brands"]), 1)
        self.assertEqual(response.data["brands"][0]["name"], "Toyota")

    def test_handle_get_colors(self):
        """Testa obtenção de cores."""
        request_data = {"action": "get_colors", "request_id": "test_123"}

        response = self.handler.handle_request(request_data)

        self.assertTrue(response.success)
        self.assertIn("colors", response.data)
        self.assertEqual(len(response.data["colors"]), 1)
        self.assertEqual(response.data["colors"][0]["name"], "Branco")

    def test_handle_get_engines(self):
        """Testa obtenção de motores."""
        request_data = {"action": "get_engines", "request_id": "test_123"}

        response = self.handler.handle_request(request_data)

        self.assertTrue(response.success)
        self.assertIn("engines", response.data)
        self.assertEqual(len(response.data["engines"]), 1)
        self.assertEqual(response.data["engines"][0]["name"], "1.6 Flex")

    def test_handle_get_car_details(self):
        """Testa obtenção de detalhes de um carro."""
        request_data = {"action": "get_car_details", "request_id": "test_123", "car_id": str(self.car.id)}

        response = self.handler.handle_request(request_data)

        self.assertTrue(response.success)
        self.assertIn("car", response.data)
        self.assertEqual(response.data["car"]["car_name"], "Corolla")
        self.assertEqual(response.data["car"]["brand"], "Toyota")

    def test_handle_get_car_details_not_found(self):
        """Testa obtenção de detalhes de carro inexistente."""
        request_data = {"action": "get_car_details", "request_id": "test_123", "car_id": str(uuid.uuid4())}

        response = self.handler.handle_request(request_data)

        self.assertFalse(response.success)
        self.assertIn("Carro não encontrado", response.error)

    def test_handle_get_filters_options(self):
        """Testa obtenção de opções de filtros."""
        request_data = {"action": "get_filters_options", "request_id": "test_123"}

        response = self.handler.handle_request(request_data)

        self.assertTrue(response.success)
        self.assertIn("filters_options", response.data)
        self.assertIn("fuel_types", response.data["filters_options"])
        self.assertIn("transmissions", response.data["filters_options"])
        self.assertIn("year_range", response.data["filters_options"])

    def test_handle_unsupported_action(self):
        """Testa ação não suportada."""
        request_data = {"action": "unsupported_action", "request_id": "test_123"}

        response = self.handler.handle_request(request_data)

        self.assertFalse(response.success)
        self.assertIn("não suportada", response.error)


class MCPRestIntegrationTestCase(TestCase):
    """Testes para integração MCP com API REST."""

    def setUp(self):
        """Configuração inicial para os testes."""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        self.integration = MCPRestIntegration(user=self.user)

    def test_validate_mcp_request_valid(self):
        """Testa validação de requisição MCP válida."""
        request_data = {"action": "search_cars", "filters": {"brand_name": "Toyota"}}

        is_valid, error = self.integration.validate_mcp_request(request_data)

        self.assertTrue(is_valid)
        self.assertIsNone(error)

    def test_validate_mcp_request_invalid_action(self):
        """Testa validação de requisição MCP com ação inválida."""
        request_data = {"action": "invalid_action"}

        is_valid, error = self.integration.validate_mcp_request(request_data)

        self.assertFalse(is_valid)
        self.assertIn("não suportada", error)

    def test_validate_mcp_request_missing_action(self):
        """Testa validação de requisição MCP sem ação."""
        request_data = {"filters": {"brand_name": "Toyota"}}

        is_valid, error = self.integration.validate_mcp_request(request_data)

        self.assertFalse(is_valid)
        self.assertIn("obrigatório", error)

    def test_validate_get_car_details_missing_car_id(self):
        """Testa validação de requisição de detalhes sem car_id."""
        request_data = {"action": "get_car_details"}

        is_valid, error = self.integration.validate_mcp_request(request_data)

        self.assertFalse(is_valid)
        self.assertIn("obrigatório", error)

    def test_validate_get_car_details_invalid_car_id(self):
        """Testa validação de requisição de detalhes com car_id inválido."""
        request_data = {"action": "get_car_details", "car_id": "invalid_uuid"}

        is_valid, error = self.integration.validate_mcp_request(request_data)

        self.assertFalse(is_valid)
        self.assertIn("UUID válido", error)


@pytest.mark.asyncio
class MCPWebSocketTestCase(APITestCase):
    """Testes para WebSocket MCP."""

    async def test_mcp_websocket_connection(self):
        """Testa conexão WebSocket MCP."""
        communicator = WebsocketCommunicator(MCPCarSocket.as_asgi(), "/ws/mcp/cars/")
        connected, subprotocol = await communicator.connect()

        self.assertTrue(connected)
        self.assertEqual(subprotocol, "MCP-V1")

        # Verificar mensagem de boas-vindas
        response = await communicator.receive_text()
        welcome_data = json.loads(response)

        self.assertEqual(welcome_data["type"], "mcp_welcome")
        self.assertEqual(welcome_data["protocol"], "MCP-V1")
        self.assertIn("search_cars", welcome_data["available_actions"])

        await communicator.disconnect()

    async def test_mcp_websocket_search_cars(self):
        """Testa busca de carros via WebSocket MCP."""
        # Criar dados de teste
        brand = Brand.objects.create(name="Toyota")
        color = Color.objects.create(name="Branco")
        engine = Engine.objects.create(name="1.6 Flex", displacement="1.6", power=120)
        car_model = CarModel.objects.create(name="Sedan")
        car_name = CarName.objects.create(name="Corolla", brand=brand)

        Car.objects.create(
            car_name=car_name,
            car_model=car_model,
            year_manufacture=2023,
            year_model=2024,
            engine=engine,
            fuel_type="flex",
            color=color,
            mileage=15000,
            doors=4,
            transmission="automatic",
            price=120000.0,
        )

        communicator = WebsocketCommunicator(MCPCarSocket.as_asgi(), "/ws/mcp/cars/")
        await communicator.connect()

        # Enviar requisição de busca
        search_request = {
            "type": "mcp_request",
            "request_id": "test_123",
            "data": {"action": "search_cars", "filters": {"brand_name": "Toyota"}},
        }

        await communicator.send_text(json.dumps(search_request))

        # Receber resposta
        response = await communicator.receive_text()
        response_data = json.loads(response)

        self.assertEqual(response_data["type"], "mcp_response")
        self.assertTrue(response_data["success"])
        self.assertIn("results", response_data["data"])
        self.assertEqual(response_data["data"]["total"], 1)

        await communicator.disconnect()

    async def test_mcp_websocket_invalid_json(self):
        """Testa WebSocket MCP com JSON inválido."""
        communicator = WebsocketCommunicator(MCPCarSocket.as_asgi(), "/ws/mcp/cars/")
        await communicator.connect()

        # Enviar JSON inválido
        await communicator.send_text("invalid json")

        # Receber resposta de erro
        response = await communicator.receive_text()
        response_data = json.loads(response)

        self.assertEqual(response_data["type"], "mcp_error")
        self.assertIn("JSON inválido", response_data["error"])

        await communicator.disconnect()

    async def test_mcp_websocket_unsupported_action(self):
        """Testa WebSocket MCP com ação não suportada."""
        communicator = WebsocketCommunicator(MCPCarSocket.as_asgi(), "/ws/mcp/cars/")
        await communicator.connect()

        # Enviar requisição com ação não suportada
        invalid_request = {"type": "mcp_request", "request_id": "test_123", "data": {"action": "unsupported_action"}}

        await communicator.send_text(json.dumps(invalid_request))

        # Receber resposta de erro
        response = await communicator.receive_text()
        response_data = json.loads(response)

        self.assertEqual(response_data["type"], "mcp_response")
        self.assertFalse(response_data["success"])
        self.assertIn("não suportada", response_data["error"])

        await communicator.disconnect()


@pytest.mark.asyncio
class MCPWebSocketV2TestCase(APITestCase):
    """Testes para WebSocket MCP V2."""

    async def test_mcp_websocket_v2_connection(self):
        """Testa conexão WebSocket MCP V2."""
        communicator = WebsocketCommunicator(MCPCarSocketV2.as_asgi(), "/ws/mcp/cars/v2/")
        connected, subprotocol = await communicator.connect()

        self.assertTrue(connected)
        self.assertEqual(subprotocol, "MCP-V2")

        await communicator.disconnect()

    async def test_mcp_websocket_v2_metrics(self):
        """Testa métricas do WebSocket MCP V2."""
        communicator = WebsocketCommunicator(MCPCarSocketV2.as_asgi(), "/ws/mcp/cars/v2/")
        await communicator.connect()

        # Enviar algumas requisições para gerar métricas
        for i in range(3):
            request = {"type": "mcp_request", "request_id": f"test_{i}", "data": {"action": "get_brands"}}
            await communicator.send_text(json.dumps(request))
            await communicator.receive_text()  # Receber resposta

        # Solicitar métricas
        metrics_request = {"type": "mcp_request", "request_id": "metrics_test", "data": {"action": "get_metrics"}}

        await communicator.send_text(json.dumps(metrics_request))

        # Receber resposta com métricas
        response = await communicator.receive_text()
        response_data = json.loads(response)

        self.assertEqual(response_data["type"], "mcp_response")
        self.assertIn("metrics", response_data["data"])
        self.assertGreater(response_data["data"]["metrics"]["total_requests"], 0)

        await communicator.disconnect()


class MCPPerformanceTestCase(TestCase):
    """Testes de performance para funcionalidades MCP."""

    def setUp(self):
        """Configuração inicial para testes de performance."""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        # Criar dados de teste em massa
        self._create_test_data()

        self.handler = CarMCPHandler(user=self.user)

    def _create_test_data(self):
        """Cria dados de teste para performance."""
        # Criar 100 marcas
        brands = []
        for i in range(100):
            brand = Brand.objects.create(name=f"Brand_{i}")
            brands.append(brand)

        # Criar 50 cores
        colors = []
        for i in range(50):
            color = Color.objects.create(name=f"Color_{i}")
            colors.append(color)

        # Criar 200 motores
        engines = []
        for i in range(200):
            engine = Engine.objects.create(name=f"Engine_{i}", displacement=f"{1.0 + i * 0.1:.1f}", power=100 + i)
            engines.append(engine)

        # Criar 100 modelos
        car_models = []
        for i in range(100):
            car_model = CarModel.objects.create(name=f"Model_{i}")
            car_models.append(car_model)

        # Criar 1000 nomes de carros
        car_names = []
        for i in range(1000):
            car_name = CarName.objects.create(name=f"Car_{i}", brand=brands[i % len(brands)])
            car_names.append(car_name)

        # Criar 10000 carros
        for i in range(10000):
            Car.objects.create(
                car_name=car_names[i % len(car_names)],
                car_model=car_models[i % len(car_models)],
                year_manufacture=2020 + (i % 4),
                year_model=2021 + (i % 4),
                engine=engines[i % len(engines)],
                fuel_type="flex" if i % 2 == 0 else "gasoline",
                color=colors[i % len(colors)],
                mileage=i * 1000,
                doors=2 + (i % 4),
                transmission="automatic" if i % 2 == 0 else "manual",
                price=50000.0 + (i * 1000),
            )

    def test_search_cars_performance(self):
        """Testa performance da busca de carros."""
        import time

        request_data = {
            "action": "search_cars",
            "request_id": "perf_test",
            "filters": {"year_manufacture_min": 2022, "price_max": 100000.0},
            "pagination": {"page": 1, "page_size": 20},
        }

        start_time = time.time()
        response = self.handler.handle_request(request_data)
        end_time = time.time()

        execution_time = end_time - start_time

        self.assertTrue(response.success)
        self.assertLess(execution_time, 2.0)  # Deve executar em menos de 2 segundos
        self.assertGreater(response.data["total"], 0)

    def test_get_brands_performance(self):
        """Testa performance da obtenção de marcas."""
        import time

        request_data = {"action": "get_brands", "request_id": "perf_test"}

        start_time = time.time()
        response = self.handler.handle_request(request_data)
        end_time = time.time()

        execution_time = end_time - start_time

        self.assertTrue(response.success)
        self.assertLess(execution_time, 1.0)  # Deve executar em menos de 1 segundo
        self.assertGreater(len(response.data["brands"]), 0)

    def test_get_filters_options_performance(self):
        """Testa performance da obtenção de opções de filtros."""
        import time

        request_data = {"action": "get_filters_options", "request_id": "perf_test"}

        start_time = time.time()
        response = self.handler.handle_request(request_data)
        end_time = time.time()

        execution_time = end_time - start_time

        self.assertTrue(response.success)
        self.assertLess(execution_time, 1.0)  # Deve executar em menos de 1 segundo
        self.assertIn("filters_options", response.data)
