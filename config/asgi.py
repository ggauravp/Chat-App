import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings") # Tells Django where to find the settings module for this project. This is necessary for Django to work properly.

django_asgi_app = get_asgi_application()# This creates an ASGI application that can handle HTTP requests using Django's standard request handling. It allows the application to serve regular web pages and APIs.

application = ProtocolTypeRouter({      # This is the main ASGI application that routes incoming connections based on their protocol type (HTTP or WebSocket).
    "http": django_asgi_app,            # Routes HTTP requests to the Django ASGI application created above.
    "websocket": AuthMiddlewareStack(   # This middleware stack ensures that WebSocket connections are authenticated, allowing you to access user information in your WebSocket consumers.
        URLRouter(                      # This routes WebSocket connections to the appropriate consumer based on the URL patterns defined in chat.routing.websocket_urlpatterns.
            chat.routing.websocket_urlpatterns
        )
    ),
})