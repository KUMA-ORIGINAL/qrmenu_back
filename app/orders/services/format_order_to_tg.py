
def format_order_details(order):
    items_details = []
    items_receipt = []

    for index, order_product in enumerate(order.order_products.all(), start=1):
        product_name = order_product.product.product_name
        count = order_product.count
        price = order_product.price
        items_details.append(
            f"{index}. *{product_name}* - {count} шт. - {price} сом"
        )
        items_receipt.append(
            f"{index}. {product_name} - {count} шт. - {price} сом"
        )

    total_price = order.total_price
    items_description = "\n".join(items_details)

    receipt_lines = [
        f"Квитанция",
        f"{'-' * 30}",
        '\n'.join(items_receipt),
        f"{'-' * 30}",
    ]

    if hasattr(order, 'venue') and order.venue.service_fee_percent:
        service_percentage = order.venue.service_fee_percent
        total_service_price = order.service_price
        receipt_lines.append(f"Обслуживание {service_percentage}%: {total_service_price} сом")

    receipt_lines.append(f"Итог: {total_price} сом")

    if order.tips_price:
        total_tips_price = order.tips_price
        receipt_lines.append(f"Чаевые: {total_tips_price} сом")

    if order.comment:
        comment = order.comment
    else:
        comment = "Не указан"

    receipt = "\n".join(receipt_lines)

    message_parts = [
        f"*{order.spot} - НОВЫЙ ЗАКАЗ #{order.id}*\n",
        f"*{order.get_service_mode_display().upper()}*\n\n",
        f"{items_description}\n\n"
    ]

    if order.phone:
        message_parts.append(f"*Номер клиента:* {order.phone}\n")

    if order.address:
        message_parts.append(f"*Адрес доставки:* {order.address}\n")

    if comment != "Не указан":
        message_parts.append(f"*Комментарий к заказу:* _{comment}_\n\n")

    message_parts.append(f"```\n{receipt}\n```")

    return ''.join(message_parts)

