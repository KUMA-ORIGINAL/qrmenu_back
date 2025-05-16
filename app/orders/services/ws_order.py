import logging
import re

from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

channel_layer = get_channel_layer()

async def notify_order_status(order):
    if channel_layer is None:
        logger.error("Channel layer is not configured.")
        return

    phone_number = re.sub(r'\D', '', order.phone)
    await channel_layer.group_send(
        f'orders_{phone_number}',
        {
            'type': 'order_status_update',
            'order_id': order.id,
            'status': order.status,
        }
    )
