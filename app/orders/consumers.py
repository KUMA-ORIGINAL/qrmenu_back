import json
import logging
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


class OrderStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            query_params = parse_qs(self.scope["query_string"].decode())
            self.phone_number = query_params.get("phone_number", [None])[0]

            if not self.phone_number:
                await self.close(code=4001)
                logger.error("Phone number not provided in query params.")
                return

            # Можно использовать номер телефона в названии группы
            self.room_group_name = f'orders_{self.phone_number}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

            logger.info(f"WebSocket connected for {self.phone_number}")

        except Exception as e:
            logger.exception(f"Ошибка подключения WebSocket: {e}")
            await self.close(code=1001)

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"WebSocket disconnected for {self.phone_number}")
        except Exception as e:
            logger.exception(f"Ошибка отключения WebSocket: {e}")

    async def order_status_update(self, event):
        try:
            await self.send(text_data=json.dumps({
                'order_id': event.get('order_id'),
                'status': event.get('status', 'unknown'),
                'status_text': event.get('status_text', 'Неизвестно'),
            }))
        except Exception as e:
            logger.exception(f"Ошибка отправки данных через WebSocket: {e}")
