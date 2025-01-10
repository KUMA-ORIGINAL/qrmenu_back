import requests
import logging

from menu.models import Category, Product, Modificator

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
            return None

    def post(self, endpoint, data, params=None):
        """Метод для отправки POST запросов."""
        params = params or {}
        params["token"] = self.API_TOKEN
        try:
            response = requests.post(f"{self.API_URL}{endpoint}", params=params, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при отправке данных в Poster: {e}")
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

    def create_new_category(self, venue, poster_category):
        new_category = Category.objects.create(
            external_id=poster_category.get('category_id'),
            category_name=poster_category.get('category_name'),
            category_photo=self.BASE_URL + str(poster_category.get('category_photo')),
            venue=venue,
            pos_system=venue.pos_system
        )
        return new_category

    def create_new_product(self, venue, product_data):
        category = (Category.objects.filter(venue=venue)
                    .get(external_id=product_data.get('menu_category_id')))
        modificators_data = product_data.get('modifications', [])

        if not modificators_data:
            product_price = product_data.get('price').get('1')
        else:
            product_price = product_data.get('price')

        new_product = Product.objects.create(
            external_id=product_data.get('product_id'),
            product_name=product_data.get('product_name'),
            product_photo=self.BASE_URL + str(product_data.get('photo')),
            product_price=product_price,
            hidden=product_data.get('hidden'),
            venue=venue,
            pos_system=venue.pos_system,
            category=category
        )
        for modificator_data in modificators_data:
            new_modificator = self.create_new_modificator(modificator_data)
            new_product.modificators.add(new_modificator)
        return new_product

    def create_new_modificator(self, modificator_data):
        new_modificator = Modificator.objects.create(
            external_id=modificator_data['modificator_id'],
            modificator_name=modificator_data['modificator_name'],
            modificator_selfprice=modificator_data['modificator_selfprice']
        )
        return new_modificator

    def get_categories(self):
        """Метод для получения категорий меню из Poster."""
        return self.get("menu.getCategories")

    def get_products(self):
        """Метод для получения продуктов из Poster."""
        return self.get("menu.getProducts")
