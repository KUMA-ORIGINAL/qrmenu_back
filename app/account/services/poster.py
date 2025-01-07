import requests

class PosterService:
    BASE_URL = 'https://joinposter.com'
    API_URL = BASE_URL + "/api/"

    def __init__(self, api_token):
        self.API_TOKEN = api_token

    def get(self, endpoint, params=None):
        if params is None:
            params = {}
        params["token"] = self.API_TOKEN
        try:
            response = requests.get(f"{self.API_URL}{endpoint}", params=params)
            response.raise_for_status()
            return response.json().get('response', [])
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе данных из Poster: {e}")
            return None

    def get_categories(self):
        """Метод для получения категорий меню из Poster."""
        return self.get("menu.getCategories")


