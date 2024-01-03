"""
ASGI config for social network project.

It exposes the ASGI callable as a module-level variable named ``application``.

"""

import os
from django.core.asgi import get_asgi_application
from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack


from socialnetwork.consumers import ChatConsumer
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')

application = get_asgi_application()


application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('ws/<int:id>', ChatConsumer.as_asgi())
        ])
    )
})
