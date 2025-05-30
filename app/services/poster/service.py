from decimal import Decimal

import requests
import logging

from menu.models import Category, Product, Modificator
from orders.models import Client
from venues.models import Spot, Table, Hall

logger = logging.getLogger(__name__)


class PosterService:
    BASE_URL = 'https://joinposter.com'
    API_URL = f"{BASE_URL}/api/"

    def __init__(self, api_token):
        self.API_TOKEN = api_token

    def get(self, endpoint, params=None):
        """Метод для отправки GET запросов."""
        params = params or {}
        params["token"] = self.API_TOKEN
        try:
            response = requests.get(f"{self.API_URL}{endpoint}", params=params)
            response.raise_for_status()  # Генерирует исключение для кода состояния >= 400
            return response.json().get('response', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе данных из Poster: {e}")

    def post(self, endpoint, data, params=None):
        """Метод для отправки POST запросов."""
        params = params or {}
        params["token"] = self.API_TOKEN

        try:
            response = requests.post(f"{self.API_URL}{endpoint}", params=params, json=data)
            logger.info(response.json())
            response.raise_for_status()
            return response.json().get('response', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при отправке данных в Poster: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Неизвестная ошибка при отправке данных в Poster: {e}", exc_info=True)
            return None

    def sync_with_poster(self, entity_type, entity_id, side_id):
        """Метод для синхронизации сущности с Poster."""
        extras = {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'extras': {'side_id': side_id}
        }

        response = self.post("application.setEntityExtras", extras)
        logger.error(response)
        if response and response.get('response') == True:
            logger.info(f"Сущность {entity_type} с ID {entity_id} успешно синхронизирована с Poster.")
            return True
        else:
            logger.error(f"Ошибка синхронизации сущности {entity_type} с ID {entity_id} с Poster.")
            return False

    def create_new_category(self, poster_category, venue, *args):
        new_category = Category.objects.create(
            external_id=poster_category.get('category_id'),
            category_name=poster_category.get('category_name'),
            category_photo=self.BASE_URL + str(poster_category.get('category_photo')),
            venue=venue
        )
        return new_category

    def create_new_product(self, product_data, venue, *args):
        modificators_data = product_data.get('modifications', [])

        if not modificators_data:
            product_price = Decimal(product_data.get('price').get('1')) / 100
        else:
            product_price = 0

        new_product = Product.objects.create(
            external_id=product_data.get('product_id'),
            product_name=product_data.get('product_name'),
            product_photo=self.BASE_URL + str(product_data.get('photo')),
            product_price=product_price,
            weight=product_data.get('out'),
            hidden=product_data.get('hidden'),
            venue=venue,
            category=args[0],
        )
        spots = args[1]
        new_product.spots.set(spots)

        for modificator_data in modificators_data:
            self.create_new_modificator(modificator_data, new_product)
        return new_product

    def create_new_modificator(self, modificator_data, new_product):
        spots = modificator_data.get('spots')
        price = Decimal(spots[0].get('price')) / 100
        Modificator.objects.create(
            external_id=modificator_data.get('modificator_id'),
            name=modificator_data.get('modificator_name'),
            price=price,
            product=new_product
        )

    def create_new_spot(self, spot_data, venue, *args):
        new_spot = Spot.objects.create(
            external_id=spot_data['spot_id'],
            name=spot_data['name'],
            address=spot_data.get('address'),
            venue=venue
        )
        return new_spot

    def create_new_table(self, table_data, venue, *args):
        new_table = Table.objects.create(
            external_id=table_data['table_id'],
            table_num=table_data.get('table_num'),
            table_title=table_data.get('table_title'),
            table_shape=table_data.get('table_shape'),
            hall=args[0],
            spot=args[1],
            venue=venue
        )
        return new_table

    def create_new_hall(self, hall_data, venue, *args):
        new_hall = Hall.objects.create(
            external_id=hall_data['hall_id'],
            hall_name=hall_data.get('hall_name'),
            spot=args[0],
            venue=venue
        )
        return new_hall

    def send_order_to_pos(self, order):
        table = order.table
        table_info = f"\nСтол: {table.table_num}" if table else ""

        comment = (
            f"Комментарий: {order.comment}\n"
            f"Обслуживание: {order.service_price}\n"
            f"Чаевые: {order.tips_price}"
            f"{table_info}"
        )
        incoming_order_data = {
            'spot_id': order.spot.external_id,
            'phone': order.phone,
            'comment': comment,
            'service_mode': order.service_mode,
        }

        products = []
        for order_product in order.order_products.all():
            product = order_product.product
            modificator = order_product.modificator
            modificator_id = modificator.external_id if modificator else None
            products.append(
                {
                    'product_id': product.external_id,
                    'count': order_product.count,
                    'modificator_id': modificator_id
                }
            )

        response = self.create_incoming_order(
            incoming_order_data=incoming_order_data,
            products=products
        )

        return response

    def create_incoming_order(self, incoming_order_data, products):
        incoming_order = {
            **incoming_order_data,
            'products': products,
        }
        response = self.post("incomingOrders.createIncomingOrder", incoming_order)
        return response

    def get_or_create_client(self, venue, poster_client_id):
        client = Client.objects.filter(
            venue=venue,
            external_id=poster_client_id
        ).first()
        poster_client_data = self.get_client_by_id(poster_client_id)[0]
        if client:
            client.firstname = poster_client_data.get('firstname', '')
            client.lastname = poster_client_data.get('lastname', '')
            client.patronymic = poster_client_data.get('patronymic', '')
            client.phone = poster_client_data.get('phone')
            client.phone_number = poster_client_data.get('phone_number')
            client.email = poster_client_data.get('email', None)
            client.birthday = poster_client_data.get('birthday') \
                if poster_client_data.get('birthday') != '0000-00-00' else None
            client.client_sex = int(poster_client_data.get('client_sex',
                                                           0))  # Преобразование значения из строки в число
            client.bonus = Decimal(poster_client_data.get('bonus', 0))
            client.total_payed_sum = Decimal(poster_client_data.get('total_payed_sum', 0)) / 100
            client.country = poster_client_data.get('country', '')
            client.city = poster_client_data.get('city', '')
            client.address = poster_client_data.get('address', '')

            client.save()
        else:
            client = Client.objects.create(
                external_id=poster_client_data.get('client_id'),
                firstname=poster_client_data.get('firstname', ''),
                lastname=poster_client_data.get('lastname', ''),
                patronymic=poster_client_data.get('patronymic', ''),
                phone=poster_client_data.get('phone'),
                phone_number=poster_client_data.get('phone_number'),
                email=poster_client_data.get('email', None),
                birthday=poster_client_data.get('birthday')
                         if poster_client_data.get('birthday') != '0000-00-00' else None,
                client_sex=int(poster_client_data.get('client_sex', 0)),  # Преобразование значения из строки в число
                bonus=Decimal(poster_client_data.get('bonus', 0)),
                total_payed_sum=Decimal(poster_client_data.get('total_payed_sum', 0)),
                country=poster_client_data.get('country', ''),
                city=poster_client_data.get('city', ''),
                address=poster_client_data.get('address', ''),
                venue=venue  # предположительно, venue уже определена в контексте
            )
        return client

    def get_categories(self):
        """Метод для получения категорий меню из Poster."""
        return self.get("menu.getCategories")

    def get_products(self):
        """Метод для получения продуктов из Poster."""
        return self.get("menu.getProducts")

    def get_spots(self):
        """Метод для получения заведений из Poster."""
        return self.get("spots.getSpots")

    def get_tables(self):
        """Метод для получения столов из Poster."""
        return self.get("spots.getTableHallTables")

    def get_halls(self):
        """Метод для получения столов из Poster."""
        return self.get("spots.getSpotTablesHalls")

    def get_incoming_order_by_id(self, order_id):
        params = {
            'incoming_order_id': order_id
        }
        return self.get("incomingOrders.getIncomingOrder", params=params)

    def get_client_by_id(self, client_id):
        params = {
            'client_id': client_id
        }
        return self.get("clients.getClient", params=params)

    def get_settings(self):
        return self.get("settings.getAllSettings")

