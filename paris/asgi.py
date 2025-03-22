import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from visas.routing import websocket_urlpatterns as visas_websocket_urlpatterns
from messege.routing import websocket_urlpatterns as messege_websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "paris.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(visas_websocket_urlpatterns + messege_websocket_urlpatterns)
        ),
    }
)
