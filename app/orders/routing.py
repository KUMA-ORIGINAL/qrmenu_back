from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/orders/", consumers.OrderStatusConsumer.as_asgi()),
]