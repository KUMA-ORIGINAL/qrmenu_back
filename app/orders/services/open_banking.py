import requests
import logging

from django.conf import settings

PAYMENT_API_URL = "https://pay.operator.kg/api/v1/payments/make-payment-link/"

logger = logging.getLogger(__name__)


def generate_payment_link(transaction, order, payment_account):
    redirect_url = (
        order.tg_redirect_url if order.is_tg_bot and order.tg_redirect_url
        else f"https://imenu.kg/orders/{order.id}"
    )

    payload = {
        "amount": str(transaction.total_price),
        "transaction_id": str(transaction.id),
        "comment": f"Оплата заказа #{transaction.id} hospital",
        "redirect_url": redirect_url,
        "token": payment_account.token,
    }

    headers = {
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(PAYMENT_API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data.get('pay_url')
        else:
            logger.error(f"Ошибка создания платёжной ссылки. Код: {response.status_code}, Ответ: {response.content}")
            return None

    except Exception as e:
        logger.error(f"Ошибка при запросе к платежному сервису: {str(e)}", exc_info=True)
        return None
