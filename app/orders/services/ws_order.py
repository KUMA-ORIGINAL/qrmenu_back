from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def notify_order_status(order_id, status):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'order_{order_id}',
        {
            'type': 'order_status_update',
            'status': status,
        }
    )
