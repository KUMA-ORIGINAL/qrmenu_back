import logging

from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

channel_layer = get_channel_layer()

async def notify_order_status(phone_number, order_id, status):
    if channel_layer is None:
        logger.error("Channel layer is not configured.")
        return

    await channel_layer.group_send(
        f'orders_{phone_number}',
        {
            'type': 'order_status_update',
            'order_id': order_id,
            'status': status,
        }
    )
