"""
Consumer WebSocket MCP (Model Context Protocol) para busca de carros em tempo real.

Este módulo implementa o consumer WebSocket que processa requisições MCP,
permitindo busca dinâmica de carros com filtros em tempo real.
"""

import json
import logging
from datetime import datetime
from typing import Any

from rest_framework.permissions import AllowAny

from apps.web_sockets.mcp_handlers import CarMCPHandler
from apps.web_sockets.views_sockets import AbstractSocket

logger = logging.getLogger(__name__)


class MCPCarSocket(AbstractSocket):
    """
    WebSocket consumer para protocolo MCP de busca de carros.

    Este consumer implementa o protocolo MCP sobre WebSocket V1,
    permitindo busca dinâmica de carros com filtros em tempo real.
    """

    current_protocol = "MCP-V1"
    permission_classes = [AllowAny]

    def __init__(self, *args, **kwargs):
        """Inicializa o consumer MCP."""
        super().__init__(*args, **kwargs)
        self.mcp_handler = None
        self.search_history = []  # Histórico de buscas por sessão

    async def send_json(self, data):
        """Envia dados como JSON via WebSocket."""
        await self.send(text_data=json.dumps(data, default=str))

    def create_error_response(self, error_message, error_code="INTERNAL_ERROR", request_id=None):
        """Cria uma resposta de erro padronizada."""
        return {
            "type": "mcp_error",
            "error": error_message,
            "error_code": error_code,
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
        }

    def create_mcp_response(self, success=True, data=None, error=None, error_code=None, request_id=None):
        """Cria uma resposta MCP padronizada."""
        return {
            "type": "mcp_response",
            "request_id": request_id,
            "success": success,
            "data": data,
            "error": error,
            "error_code": error_code,
            "timestamp": datetime.now().isoformat(),
        }

    def create_search_entry(self, request_data, response):
        """Cria uma entrada de histórico de busca padronizada."""
        return {
            "timestamp": datetime.now().isoformat(),
            "filters": request_data.get("filters", {}),
            "pagination": request_data.get("pagination", {}),
            "results_count": response.get("data", {}).get("total", 0) if response.get("success") else 0,
            "success": response.get("success", False),
        }

    async def connect(self):
        """Handle WebSocket connection para MCP."""
        # Usar o método connect do AbstractSocket
        await super().connect()

        # Inicializar handler MCP
        self.mcp_handler = CarMCPHandler(user=self.user)

        # Enviar mensagem de boas-vindas MCP
        welcome_message = {
            "type": "mcp_welcome",
            "message": "Conectado ao protocolo MCP para busca de carros",
            "protocol": self.current_protocol,
            "available_actions": [
                "search_cars",
                "get_brands",
                "get_colors",
                "get_engines",
                "get_car_details",
                "get_filters_options",
            ],
            "user": str(self.user) if self.user else "anonymous",
            "room": self.room,
            "timestamp": datetime.now().isoformat(),
        }

        await self.send_json(welcome_message)

    async def receive(self, text_data=None, bytes_data=None):
        """Processa mensagens MCP recebidas do cliente."""
        try:
            if text_data:
                # Parse da mensagem JSON
                try:
                    message_data = json.loads(text_data)
                except json.JSONDecodeError as e:
                    error_response = self.create_error_response(f"JSON inválido: {e!s}", "INVALID_JSON")
                    await self.send_json(error_response)
                    return

                # Verificar se é uma requisição MCP
                if message_data.get("type") == "mcp_request":
                    await self._handle_mcp_request(message_data)
                else:
                    # Usar o método receive do AbstractSocket para mensagens normais
                    await super().receive(text_data, bytes_data)

        except Exception as e:
            logger.error(f"Erro ao processar mensagem MCP: {e}", exc_info=True)
            error_response = self.create_error_response(f"Erro interno: {e!s}")
            await self.send_json(error_response)

    async def _handle_mcp_request(self, message_data: dict[str, Any]):
        """Processa uma requisição MCP específica."""
        try:
            # Extrair dados da requisição
            request_data = message_data.get("data", {})
            request_id = message_data.get("request_id")

            # Adicionar request_id se não fornecido
            if not request_id:
                request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

            # Construir estrutura completa para o serializer
            full_request_data = {"request_id": request_id, "data": request_data}

            # Processar requisição via handler MCP
            response = await self.mcp_handler.handle_request(full_request_data)

            # Adicionar ao histórico de buscas se for uma busca
            if request_data.get("action") == "search_cars":
                self._add_to_search_history(request_data, response)

            # Enviar resposta MCP
            await self.send_json(response)

        except Exception as e:
            logger.error(f"Erro ao processar requisição MCP: {e}", exc_info=True)
            error_response = self.create_error_response(
                f"Erro ao processar requisição: {e!s}", "REQUEST_PROCESSING_ERROR", message_data.get("request_id")
            )
            await self.send_json(error_response)

    def _add_to_search_history(self, request_data: dict[str, Any], response):
        """Adiciona busca ao histórico da sessão."""
        try:
            search_entry = self.create_search_entry(request_data, response)

            # Manter apenas os últimos 50 registros
            self.search_history.append(search_entry)
            if len(self.search_history) > 50:
                self.search_history = self.search_history[-50:]

        except Exception as e:
            logger.warning(f"Erro ao adicionar ao histórico de buscas: {e}")

    async def get_search_history(self):
        """Retorna o histórico de buscas da sessão."""
        history_response = self.create_mcp_response(
            data={
                "action": "get_search_history",
                "history": self.search_history,
                "total_searches": len(self.search_history),
            }
        )
        await self.send_json(history_response)

    async def clear_search_history(self):
        """Limpa o histórico de buscas da sessão."""
        self.search_history = []
        clear_response = self.create_mcp_response(
            data={"action": "clear_search_history", "message": "Histórico de buscas limpo"}
        )
        await self.send_json(clear_response)

    async def send_messages(self, dt: dict):
        """Envia mensagens para o cliente (compatibilidade com AbstractSocket)."""
        data = dt.copy()
        if "data" in data and isinstance(data["data"], str):
            data["data"] = json.loads(data["data"])
        data.pop("type", None)
        await self.send_json(data)

    async def broadcast_to_room(self, message):
        """Envia uma mensagem para todos os usuários na sala."""
        broadcast_message = {
            "type": "broadcast",
            "message": message,
            "user": str(self.user) if self.user else "anonymous",
            "room": self.room,
            "timestamp": datetime.now().isoformat(),
        }

        await self.channel_layer.group_send(
            self.room, {"type": "group_message", "data": json.dumps(broadcast_message, default=str)}
        )

    async def group_message(self, event):
        """Handle group messages (broadcast)."""
        message = event["data"]
        await self.send(text_data=message)

    async def disconnect(self, code):
        """Handle WebSocket disconnection."""
        # Log da desconexão com estatísticas MCP
        total_searches = len(self.search_history)
        logger.debug(f"Usuário MCP {self.user} desconectado da sala {self.room}. Total de buscas: {total_searches}")

        # Usar o método disconnect do AbstractSocket
        await super().disconnect(code)
