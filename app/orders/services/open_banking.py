import requests
import json
import logging

from django.conf import settings

PAYMENT_API_URL = "https://pay.operator.kg/api/v1/payments/make-payment-link/"
PAYMENT_API_TOKEN = settings.PAYMENT_API_TOKEN

logger = logging.getLogger(__name__)


def generate_payment_link(transaction):
    payload = {
        "amount": str(transaction.total_price),
        "transaction_id": str(transaction.id),
        "comment": f"Оплата заказа #{transaction.id} hospital",
        "redirect_url": f"https://hospital.operator.kg/",
        'token': PAYMENT_API_TOKEN,
    }

    headers = {
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(PAYMENT_API_URL, data=json.dumps(payload), headers=headers)

        if response.status_code == 200:
            return response.text.strip()
        else:
            logger.error(f"Ошибка создания платёжной ссылки. Код: {response.status_code}, Ответ: {response.content}")
            return None

    except Exception as e:
        logger.error(f"Ошибка при запросе к платежному сервису: {str(e)}", exc_info=True)
        return None
