import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
from .consumer import LlmConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'demo.settings')

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter([
                    path('llm-websocket/<str:call_id>/', LlmConsumer.as_asgi()),
                ])
            )
        ),
    }
)
