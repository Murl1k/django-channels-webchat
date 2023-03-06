from django.urls import path
from .consumers import consumers

websocket_urlpatterns = [
    path('chat/', consumers.ChatConsumer.as_asgi())
]