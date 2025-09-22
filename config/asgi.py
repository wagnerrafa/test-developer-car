"""
ASGI configuration for WebSocket support.

This module configures the ASGI application to handle both HTTP and WebSocket
connections, including authentication and session management.
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.sessions import SessionMiddlewareStack
from django.core.asgi import get_asgi_application

from apps.web_sockets.urls_sockets import websockets

django_asgi_app = get_asgi_application()

protocol_routers = {
    # WebSocket urls handler
    "websocket": AllowedHostsOriginValidator(SessionMiddlewareStack(AuthMiddlewareStack(websockets))),
    "http": django_asgi_app,
}
application = ProtocolTypeRouter(protocol_routers)
