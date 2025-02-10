import json
from channels.generic.websocket import AsyncWebsocketConsumer


class OrderStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'order_{self.order_id}'

        try:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        except Exception as e:
            # Обрабатываем ошибки подключения
            await self.close(code=1001)
            print(f"Ошибка подключения: {e}")

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            print(f"Ошибка отключения: {e}")

    # Получение сообщения из группы и отправка на WebSocket
    async def order_status_update(self, event):
        status = event.get('status', 'unknown')  # Подстраховка на случай, если статус не передан
        try:
            await self.send(text_data=json.dumps({
                'status': status
            }))
        except Exception as e:
            print(f"Ошибка отправки данных: {e}")
