import requests

class PosterService:
    BASE_URL = "https://joinposter.com/api/"
    API_TOKEN = ""

    def __init__(self, api_token):
        self.API_TOKEN = api_token


class PosterMenuService(PosterService):
    def __init__(self, api_token):
        super().__init__(api_token)
        self.BASE_URL = self.BASE_URL + 'menu'

    def get_categories(self):
        """Метод для получения категорий меню из Poster."""
        try:
            response = requests.get(
                f"{self.BASE_URL}/getCategories",  # Правильный путь к API
                params={"token": self.API_TOKEN}
            )
            response.raise_for_status()  # Проверка на ошибки HTTP
            return response.json().get('response', [])
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе данных из Poster: {e}")
            return []
