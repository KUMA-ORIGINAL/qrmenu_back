from datetime import datetime

import requests
import json
import logging

from django.conf import settings
from django.utils import timezone

from ..models import Receipt
from ..models import ReceiptPrinter

logger = logging.getLogger(__name__)


def send_receipt_to_webhook(order, venue, spot):
    try:
        receipt_printer = ReceiptPrinter.objects.filter(venue=venue).first()

        timezone.activate('Asia/Bishkek')  # Пример для часового пояса UTC+6
        order_date_local = timezone.localtime(order.created_at)

        header = (
                "<F3232><CENTER><FB>iMENU.KG</FB> ЗАКАЗ #" + str(order.id) + "\\r</CENTER></F3232>"
                f"<F3232><CENTER><FB>АДРЕС: {spot.address}\\r</FB></CENTER></F3232>"
                "<F3232><CENTER><FB>СТОЛ: ВЫНОС\\r</FB></CENTER></F3232>"
        )
        order_items = "".join([
            f"<F2424>{idx + 1}. {op.product.product_name} - {op.count} шт.\\r</F2424>"
            for idx, op in enumerate(order.order_products.all())
        ])
        full_order_details = header + order_items

        order_count = order.order_products.count()

        receipt_data = {
            "request_id": f"rq_{order.id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "amount": str(order.total_price),
            "terminal_id": receipt_printer.printer_id,  # Номер принтера
            "company_name": venue.company_name,
            "company_id": '23412341234124234',
            "company_address": spot.address,
            "order_date": order_date_local.strftime('%d.%m.%Y'),
            "order_time": order_date_local.strftime('%H:%M:%S'),
            "tr_id": f"rq_{order.id}",
            "tr_type": 'Платеж по QR',
            "order_count": f"{order_count}",
            "order_items": full_order_details
        }

        response = requests.post(settings.RECEIPT_WEBHOOK_URL, data=json.dumps(receipt_data), headers={"Content-Type": "application/json"})

        if response.status_code == 200:
            logger.info(f"Receipt sent successfully: {response.content}")

            Receipt.objects.create(
                order=order,
                receipt_printer=receipt_printer,
                venue=order.venue,
                amount=order.total_price,
                order_count=order_count,
                payload=receipt_data,  # Сохраняем JSON-параметры чека
            )
            return True

        else:
            logger.error(f"Failed to send receipt. Status code: {response.status_code}, Response: {response.content}")
            return False

    except Exception as e:
        logger.error(f"Error sending receipt: {str(e)}", exc_info=True)
        return False
