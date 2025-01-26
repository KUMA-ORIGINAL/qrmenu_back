import json
from channels.generic.websocket import AsyncWebsocketConsumer


class OrderStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Получаем ID заказа из параметров соединения WebSocket, если он передан
        self.room_group_name = f'order_'

        # Присоединяемся к группе, связанной с заказом
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Отключаемся от группы
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Получение сообщения из группы и отправка на WebSocket
    async def order_status_update(self, event):
        status = event['status']
        await self.send(text_data=json.dumps({
            'status': status
        }))

