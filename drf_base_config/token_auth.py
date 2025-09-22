"""
Token authentication middleware for Django Channels.

This module provides token-based authentication for WebSocket connections
using Django REST Framework tokens.
"""

from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token


@database_sync_to_async
def get_user(token):
    """Get user by token key."""
    try:
        return Token.objects.get(key=token).user
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware:
    """Token authorization middleware for Django Channels 2."""

    def __init__(self, inner):
        """Initialize the middleware."""
        self.inner = inner

    async def __call__(self, scope, receive, send):
        """Process the WebSocket connection with token authentication."""
        query_string = scope["query_string"]
        parsed_query = parse_qs(query_string)
        token_key = parsed_query.get(b"token")
        if token_key:
            token_key = token_key[0].decode()
            try:
                user = await get_user(token_key)
                scope["user"] = user
            except Token.DoesNotExist:
                scope["user"] = AnonymousUser()
        return await self.inner(scope, receive, send)


def token_auth_middleware_stack(inner):
    """Create a token auth middleware stack."""
    return TokenAuthMiddleware(inner)
