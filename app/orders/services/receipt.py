import time
import uuid
from datetime import datetime
import json
import logging
import atexit

import paho.mqtt.client as mqtt
from django.conf import settings
from django.utils import timezone

from ..models import Receipt
from ..models import ReceiptPrinter

logger = logging.getLogger(__name__)


class MQTTClient:
    def __init__(self):
        self.client = None
        self.initialized = False

    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            logger.info('Connected to MQTT broker successfully')
        else:
            logger.error(f'Bad connection. Code: {reason_code}')

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        if reason_code != 0:
            logger.warning(f'Unexpected disconnection (rc={reason_code})')

    def on_message(self, client, userdata, msg):
        logger.info(f'Received message on topic: {msg.topic} with payload: {msg.payload.decode()}')

    def initialize(self):
        if self.initialized:
            return

        try:
            self.client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id=f"receipt_sender_{uuid.uuid4()}",
                transport="tcp",
            )
            self.client.username_pw_set(settings.RECEIPT_MQTT_USERNAME, settings.RECEIPT_MQTT_PASSWORD)

            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message

            self.client.connect(
                host=settings.RECEIPT_MQTT_BROKER,
                port=settings.RECEIPT_MQTT_PORT,
                keepalive=60
            )
            self.client.loop_start()
            self.initialized = True
            logger.info('MQTT client initialized and connected')
        except Exception as e:
            logger.error(f'Failed to connect MQTT client: {str(e)}', exc_info=True)
            self.initialized = False

    def disconnect(self):
        if self.client and self.initialized:
            try:
                self.client.loop_stop()
                self.client.disconnect()
                logger.info('MQTT client disconnected')
                self.initialized = False
            except Exception as e:
                logger.error(f'Error disconnecting MQTT client: {str(e)}', exc_info=True)

    def reconnect(self):
        if not self.initialized or not self.client or not self.client.is_connected():
            try:
                if self.client:
                    self.client.reconnect()
                    logger.info('Successfully reconnected to MQTT broker')
                else:
                    self.initialize()
            except Exception as e:
                logger.error(f'Reconnect failed: {str(e)}', exc_info=True)
                return False
        return True

    def send_message(self, topic, payload, qos=1):
        if not self.initialized:
            self.initialize()

        if not self.client.is_connected():
            if not self.reconnect():
                return False

        try:
            result = self.client.publish(topic, payload, qos=qos)
            result.wait_for_publish()

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info("Message successfully sent to topic!")
                return True
            else:
                logger.error(f"Error sending message: code {result.rc}")
                return False
        except Exception as e:
            logger.error(f"Error publishing message: {str(e)}", exc_info=True)
            return False


# Create a singleton instance
mqtt_client = MQTTClient()


def send_receipt_to_mqtt(order, venue):
    try:
        # Get the receipt printer
        receipt_printer = ReceiptPrinter.objects.filter(venue=venue).first()

        if not receipt_printer:
            logger.error(f"No receipt printer found for venue {venue.id}")
            return False

        if not receipt_printer.topic:
            logger.error(f"No topic configured for receipt printer {receipt_printer.id}")
            return False

        timezone.activate('Asia/Bishkek')
        order_date_local = timezone.localtime(order.created_at)

        address = order.spot.address if order.spot.address else "Адрес не указан"
        delivery_address = order.address if order.address else "Адрес не указан"
        service_mode = order.get_service_mode_display().upper()

        printdata = (
            f"<LOGO>printest</LOGO><F3232><CENTER>{venue.company_name}\r</CENTER></F3232>"
            f"<F2424><CENTER>{order_date_local.strftime('%d.%m.%Y             %H:%M:%S')}</CENTER></F2424>\r"
            f"<F2424>Терминал ID: {receipt_printer.topic}\r</F2424>"
            f"<F2424>Адрес: {address}\r</F2424>"
            f"<F2424>Тип операции: Оплата elQR\r</F2424>"
            f"<F2424>ID транзакции: trx_{order.id}\r</F2424>"
            f"<F3232><CENTER>----------------------------\r</CENTER></F3232>"
            f"<F3232><FB><CENTER>{service_mode}\r</CENTER></FB></F3232>"
            f"<F2424>Заказ #{order.id}\r</F2424>"
            f"<F2424>Клиент: {order.phone}\r\r</F2424>"
        )

        order_items = "<F2424>"
        for idx, op in enumerate(order.order_products.all(), start=1):
            product_name = f"{op.product.product_name}"
            if op.modificator:
                product_name = product_name + f" ({op.modificator})"
            order_items += f"{idx}. {product_name} x{op.count} {op.total_price} сом\r"

        if order.service_price and order.service_price > 0:
            order_items += f"Обслуживание: {order.service_price} сом"
        order_items += "</F2424>\r"
        order_items += f"<F2424><FB>Итого: {order.total_price} сом</FB></F2424>\r"

        comment_text = f"<F2424>\rКомментарий: {order.comment}</F2424>" if order.comment else ""

        total_sum = (
            comment_text +
            f"<F2424><CENTER>\rАдрес доставки: {delivery_address}\r</CENTER></F2424>"
            f"<F3232><CENTER>----------------------------\r</CENTER></F3232>"
            f"<F3232><CENTER>{order.total_price} сом\r</CENTER></F3232>"
            f"<F3232><FB><CENTER>УСПЕШНО\r</CENTER></FB></F3232>"
            f"<F3232><CENTER>----------------------------\r</CENTER></F3232>"
            f"<CENTER>Подпись клиента не требуется\r</CENTER>"
            f"<F3232><CENTER>----------------------------\r\r\r</CENTER></F3232>"
        )

        printdata = printdata + order_items + total_sum

        # Format payload
        payload_data = {
            "request_id": f"rq_{order.id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "biz_type": "1",
            "broadcast_type": "0",
            "money": str(order.total_price),
            "printdata": printdata.strip()
        }

        payload_json = json.dumps(payload_data, ensure_ascii=False)
        topic = receipt_printer.topic

        # Send the message
        result = mqtt_client.send_message(topic, payload_json)

        if result:
            logger.info(f"Receipt sent successfully via MQTT to topic {topic}")

            # Save the receipt
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


def send_test_receipt(venue):
    """
    Формирует и отправляет тестовый чек на настроенный принтер через MQTT.
    """
    try:
        # Находим принтер
        receipt_printer = ReceiptPrinter.objects.filter(venue=venue).first()
        if not receipt_printer:
            logger.error(f"Нет принтера для заведения {venue.id}")
            return False
        if not receipt_printer.topic:
            logger.error(f"Нет топика для принтера {receipt_printer.id}")
            return False

        timezone.activate('Asia/Bishkek')
        now_local = timezone.localtime(timezone.now())

        # Формируем тестовый чек
        printdata = (
            f"<LOGO>printest</LOGO>"
            f"<F3232><CENTER>{venue.company_name} (ТЕСТ)</CENTER></F3232>\r"
            f"<F2424><CENTER>{now_local.strftime('%d.%m.%Y   %H:%M:%S')}</CENTER></F2424>\r"
            f"<F2424>Терминал ID: {receipt_printer.topic}</F2424>\r"
            f"<F3232><CENTER>----------------------------</CENTER></F3232>\r"
            f"<F3232><FB><CENTER>ТЕСТОВЫЙ ЗАКАЗ</CENTER></FB></F3232>\r"
            f"<F2424>Заказ #TEST\r"
            f"<F2424>Клиент: +996 XXX XXX XXX</F2424>\r\r"
        )

        order_items = "<F2424>1. Тестовый товар x1 100 сом\r</F2424>\r"
        order_items += f"<F2424><FB>Итого: 100 сом</FB></F2424>\r"

        total_sum = (
            f"<F3232><CENTER>----------------------------</CENTER></F3232>\r"
            f"<F3232><CENTER>100 сом</CENTER></F3232>\r"
            f"<F3232><FB><CENTER>УСПЕШНО (ТЕСТ)</CENTER></FB></F3232>\r"
            f"<F3232><CENTER>----------------------------</CENTER></F3232>\r"
            f"<CENTER>Подпись клиента не требуется</CENTER>\r"
            f"<F3232><CENTER>----------------------------\r\r\r</CENTER></F3232>"
        )

        printdata = printdata + order_items + total_sum

        # Формируем payload
        payload_data = {
            "request_id": f"rq_TEST_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "biz_type": "1",
            "broadcast_type": "0",
            "money": "100",
            "printdata": printdata.strip()
        }

        payload_json = json.dumps(payload_data, ensure_ascii=False)
        topic = receipt_printer.topic

        # Отправляем
        success = mqtt_client.send_message(topic, payload_json)

        if success:
            logger.info(f"Тестовый чек успешно отправлен в топик {topic}")
            return True
        else:
            logger.error(f"Не удалось отправить тестовый чек в топик {topic}")
            return False

    except Exception as e:
        logger.error(f"Ошибка при отправке тестового чека: {str(e)}", exc_info=True)
        return False
