"""
WebSocket consumers and related functionality for real-time communication.

This module provides WebSocket consumers for handling real-time communication
between clients and the server, including room-based messaging and user
identification.
"""

import json
import logging
from datetime import datetime

import channels
import channels.layers
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.permissions import AllowAny

from drf_base_apps.utils import get_user_model

User = get_user_model()


class SocketsLayout:
    """Layout base para envio de mensagens via WebSocket."""

    type = "send_messages"

    def get_layout(self, channel, data, channel_type="array"):
        """Get the layout for WebSocket message sending."""
        try:
            data = json.loads(data)
        except (TypeError, KeyError, ValueError) as e:
            logging.debug(e)
        return {
            "type": self.type,
            "channel": channel,
            "data": json.dumps(data, default=str),
            "channel_type": channel_type,
        }

    def send_data(self, room, channel, serialized_data, channel_type):
        """Send data to a specific room via WebSocket."""
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(str(room), self.get_layout(channel, serialized_data, channel_type))


class AbstractSocket(SocketsLayout, AsyncWebsocketConsumer):
    """Classe base para WebSocket consumers com funcionalidades de sala."""

    current_protocol = "V1"

    def __init__(self, *args, **kwargs):
        """Initialize the WebSocket consumer."""
        super().__init__(args, kwargs)
        self.room = None
        self.user = None

    async def get_user(self):
        """Get the user from the WebSocket scope."""
        try:
            return self.scope["user"]
        except KeyError:
            return None

    async def get_room(self):
        """
        Determina a sala baseada na sessão do usuário.

        Estratégias de sala:
        1. Se usuário autenticado: usa user_id + session_key
        2. Se usuário anônimo: usa anon_id do cookie ou session_key
        3. Fallback: usa 'general'
        """
        user = await self.get_user()

        # Obter session_key da sessão do Django
        session = self.scope.get("session", {})
        session_key = session.session_key if session else None

        # Se usuário autenticado, usar user_id + session_key
        if user and hasattr(user, "id") and user.id and not user.is_anonymous:
            return f"user_{user.id}_{session_key or 'default'}"

        # Se usuário anônimo, usar anon_id do cookie ou session_key
        cookies = self.scope.get("cookies", {})
        anon_id = cookies.get("anon_id")

        if anon_id:
            return f"anonymous_{anon_id}"
        elif session_key:
            return f"anonymous_{session_key}"

        # Fallback para sala geral (caso raro onde não há identificação)
        return "general"

    async def connect(self):
        """Handle WebSocket connection."""
        user = await self.get_user()
        self.user = user
        self.room = await self.get_room()

        # Debug: mostrar informações da sessão
        session = self.scope.get("session", {})
        session_key = session.session_key if session else None
        cookies = self.scope.get("cookies", {})
        anon_id = cookies.get("anon_id")

        if user and hasattr(user, "id") and user.id and not user.is_anonymous:
            user_info = f"ID: {user.id}"
        else:
            if anon_id:
                user_info = f"Anônimo (ID: {anon_id[:8]})"
            elif session_key:
                user_info = f"Anônimo (sessão: {session_key[:8]})"
            else:
                user_info = "Anônimo (sem identificação)"

        logging.debug(f"Usuário {user_info} conectando na sala {self.room}")
        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept(self.current_protocol)
        logging.debug(f"Usuário {user_info} conectado na sala {self.room}")

    async def receive(self, text_data=None, bytes_d=None):
        """Processa mensagens recebidas do cliente."""
        try:
            if text_data:
                logging.debug(f"Mensagem recebida de {self.user}: {text_data}")

                # Parse da mensagem JSON se possível
                try:
                    message_data = json.loads(text_data)
                    message_type = message_data.get("type", "message")
                    message_content = message_data.get("data", text_data)
                except json.JSONDecodeError:
                    message_type = "message"
                    message_content = text_data

                # Echo da mensagem de volta para o cliente
                response = {
                    "type": "echo",
                    "original_message": message_content,
                    "message_type": message_type,
                    "user": str(self.user) if self.user else "anonymous",
                    "room": self.room,
                    "timestamp": str(datetime.now()),
                }

                await self.send(text_data=json.dumps(response, default=str))

                # Se for uma mensagem de broadcast, enviar para toda a sala
                if message_type == "broadcast":
                    await self.broadcast_to_room(message_content)

        except Exception as e:
            logging.error(f"Erro ao processar mensagem: {e}")
            await self.send(text_data=json.dumps({"type": "error", "message": f"Erro ao processar mensagem: {e!s}"}))

    async def send_messages(self, dt: dict):
        """Envia mensagens para o cliente."""
        data = dt.copy()
        if "data" in data and isinstance(data["data"], str):
            data["data"] = json.loads(data["data"])
        data.pop("type", None)
        await self.send(text_data=json.dumps(data, default=str))

    async def broadcast_to_room(self, message):
        """Envia uma mensagem para todos os usuários na sala."""
        broadcast_message = {
            "type": "broadcast",
            "message": message,
            "user": str(self.user) if self.user else "anonymous",
            "room": self.room,
            "timestamp": str(datetime.now()),
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
        if self.room:
            await self.channel_layer.group_discard(self.room, self.channel_name)
        logging.debug(f"Usuário {self.user} desconectado da sala {self.room}")


class GeneralSocket(AbstractSocket):
    """WebSocket consumer para sala individual."""

    current_protocol = "V1"
    channel_layer_alias = "general"
    permission_classes = [AllowAny]
