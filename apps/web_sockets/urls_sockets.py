"""
WebSocket URL routing configuration.

This module defines the URL patterns for WebSocket connections and routes
them to appropriate consumer classes.
"""

from channels.routing import URLRouter
from django.urls import path

from apps.web_sockets.views_sockets import GeneralSocket
from config.settings import BASE_SOCKETS

websockets = URLRouter(
    [
        path(f"{BASE_SOCKETS}general/", GeneralSocket.as_asgi()),
    ]
)
