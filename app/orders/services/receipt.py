import time
from datetime import datetime
import json
import logging

import paho.mqtt.client as mqtt
from django.conf import settings
from django.utils import timezone

from ..models import Receipt
from ..models import ReceiptPrinter

logger = logging.getLogger(__name__)


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        logger.info('Connected to MQTT broker successfully')
    else:
        logger.error(f'Bad connection. Code: {reason_code}')


def on_disconnect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        logger.warning(f'Unexpected disconnection (rc={reason_code}). Trying to reconnect...')
        while True:
            try:
                time.sleep(5)
                client.reconnect()
                logger.info('Successfully reconnected to MQTT broker.')
                break
            except Exception as e:
                logger.error(f'Reconnect failed: {str(e)}', exc_info=True)
                time.sleep(5)


def on_message(client, userdata, msg):
    logger.info(f'Received message on topic: {msg.topic} with payload: {msg.payload.decode()}')


mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    # client_id="mqttx_be0e1ee",
    clean_session=True,
)
mqtt_client.username_pw_set(settings.RECEIPT_MQTT_USERNAME, settings.RECEIPT_MQTT_PASSWORD)

mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_message = on_message

try:
    mqtt_client.connect(
        host=settings.RECEIPT_MQTT_BROKER,
        port=settings.RECEIPT_MQTT_PORT,
        keepalive=60
    )
    logger.info('MQTT client initialized and connected')
except Exception as e:
    logger.error(f'Failed to connect MQTT client: {str(e)}', exc_info=True)


def send_receipt_to_mqtt(order, venue):
    try:
        # Получаем принтер
        receipt_printer = ReceiptPrinter.objects.filter(venue=venue).first()

        if not receipt_printer:
            logger.error(f"No receipt printer found for venue {venue.id}")
            return False

        if not receipt_printer.topic:
            logger.error(f"No topic configured for receipt printer {receipt_printer.id}")
            return False

        timezone.activate('Asia/Bishkek')
        order_date_local = timezone.localtime(order.created_at)

        address = order.spot.address if order.spot else "Адрес не указан"
        delivery_address = order.address if order.address else "Адрес не указан"

        # Заголовок
        printdata = (
            # "<F3232><CENTER>----------------------------</CENTER></F3232>\r"
            f"<LOGO>printest</LOGO><F3232><CENTER>{venue.company_name}\r</CENTER></F3232>"
            f"<F2424><CENTER>{order_date_local.strftime('%d.%m.%Y             %H:%M:%S')}</CENTER></F2424>\r"
            f"<F2424>Терминал ID: {receipt_printer.topic}\r</F2424>"
            f"<F2424>Адрес: {address}\r</F2424>"
            f"<F2424>Тип операции: Оплата elQR\r</F2424>"
            f"<F2424>ID транзакции: trx_{order.id}\r</F2424>"
            f"<F3232><CENTER>----------------------------\r</CENTER></F3232>"
            f"<F2424>Заказ #{order.id}\r</F2424>"
            f"<F2424>Клиент: {order.phone}\r\r</F2424>"
        )

        order_items = "<F2424>"
        for idx, op in enumerate(order.order_products.all(), start=1):
            order_items += f"{idx}. {op.product.product_name} x{op.count} {op.total_price} сом\r"
        order_items += "</F2424>"

        total_sum = (
            f"<F2424><CENTER>\rАдрес доставки: {delivery_address}\r</CENTER></F2424>"
            f"<F3232><CENTER>----------------------------\r</CENTER></F3232>"
            f"<F3232><CENTER>{order.total_price} сом\r</CENTER></F3232>"
            f"<F3232><FB><CENTER>УСПЕШНО\r</CENTER></FB></F3232>"
            f"<F3232><CENTER>----------------------------\r</CENTER></F3232>"
            f"<CENTER>Подпись клиента не требуется\r</CENTER>"
            f"<F3232><CENTER>----------------------------\r\n\n</CENTER></F3232>"
        )

        printdata = printdata + order_items + total_sum

        # Формируем payload
        payload_data = {
            "request_id": f"rq_{order.id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "biz_type": "1",
            "broadcast_type": "1",
            "money": str(order.total_price),
            "printdata": printdata.strip()
        }

        payload_json = json.dumps(payload_data, ensure_ascii=False)

        topic = receipt_printer.topic
        result = mqtt_client.publish(topic, payload_json)

        mqtt_client.loop_stop()

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info("Сообщение успешно отправлено в топик!")
        else:
            logger.error(f"Ошибка отправки сообщения: код {result.rc}")

        if result:
            logger.info(f"Receipt sent successfully via MQTT to topic {topic}")

            # Cохраняем
            Receipt.objects.create(
                order=order,
                receipt_printer=receipt_printer,
                venue=venue,
                amount=order.total_price,
                order_count=order.order_products.count(),
                payload=payload_data,
            )
            return True
        else:
            logger.error(f"Failed to publish receipt to MQTT topic {topic}")
            return False

    except Exception as e:
        logger.error(f"Error sending receipt via MQTT: {str(e)}", exc_info=True)
        return False
