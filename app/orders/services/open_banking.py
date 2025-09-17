import requests
import logging

PAYMENT_API_URL = "https://pay.operator.kg/api/v1/payments/make-payment-link/"
logger = logging.getLogger(__name__)


def generate_payment_link(transaction, order, payment_account):
    if not payment_account:
        logger.error(f"Не найден платёжный аккаунт для заведения {order.venue}")
        return None

    redirect_url = (
        order.tg_redirect_url if order.is_tg_bot and order.tg_redirect_url
        else f"https://imenu.kg/orders/{order.id}"
    )

    payload = {
        "amount": str(transaction.total_price),
        "transaction_id": str(transaction.id),
        "comment": f"Оплата заказа #{transaction.id}",
        "redirect_url": redirect_url,
        "token": payment_account.token,
    }

    try:
        response = requests.post(
            PAYMENT_API_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10  # ⏱️ обязательно
        )
        response.raise_for_status()  # выбросит исключение если 4xx/5xx

        data = response.json()
        pay_url = data.get('pay_url')

        if not pay_url:
            logger.error(f"API не вернул pay_url. Ответ: {data}")
            return None

        # сохраняем URL в транзакцию
        transaction.payment_url = pay_url
        transaction.save(update_fields=["payment_url"])

        return pay_url

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при запросе к платежному сервису: {e}", exc_info=True)
        return None