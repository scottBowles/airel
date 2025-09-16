"""
ASGI config for website project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from strawberry.channels import GraphQLWSConsumer

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Import schema after Django is initialized
from website.types import schema

# Create WebSocket routing patterns
from django.urls import path

websocket_urlpatterns = [
    path("graphql/", GraphQLWSConsumer.as_asgi(schema=schema)),
]

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,  # All HTTP requests go to Django (same as WSGI)
        "websocket": AuthMiddlewareStack(  # WebSocket requests with auth
            URLRouter(websocket_urlpatterns)
        ),
    }
)
