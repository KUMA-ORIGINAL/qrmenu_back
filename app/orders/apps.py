import atexit

from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        from .services import mqtt_client

        mqtt_client.initialize()

        atexit.register(mqtt_client.disconnect)