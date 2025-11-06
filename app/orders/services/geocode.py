import logging
from urllib.parse import quote_plus
import requests

logger = logging.getLogger(__name__)


def geocode_osm(address: str):
    """Ищет координаты по адресу через OpenStreetMap (Nominatim)."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": address, "format": "json", "limit": 1}
    headers = {"User-Agent": "DeliveryBot/1.0 (asanovkurmanbek342@gmail.com)"}

    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()

    logger.info(f"Geocoded '{address}' -> {data}")
    print(data)

    if data:
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return lat, lon
    return None, None


def build_yandex_taxi_link(order):
    if getattr(order, "service_mode", None) != 3:
        return None

    from_address = getattr(order.spot, "address", "") or ""
    to_address = getattr(order, "address", "") or ""

    if not from_address or not to_address:
        logger.warning(f"[Order {order.id}] Нет адресов для создания ссылки.")
        return None

    start_lat, start_lon = geocode_osm(from_address)
    end_lat, end_lon = geocode_osm(to_address)

    # если координаты получены — используем маршрут по координатам
    if all([start_lat, start_lon, end_lat, end_lon]):
        link = (
            "https://3.redirect.appmetrica.yandex.com/route"
            f"?start-lat={start_lat}&start-lon={start_lon}"
            f"&end-lat={end_lat}&end-lon={end_lon}"
            "&ref=YumPosBot&appmetrica_tracking_id=1178268795219780156"
        )
    else:
        # иначе формируем по адресам
        link = (
            "https://3.redirect.appmetrica.yandex.com/route?"
            f"from={quote_plus(from_address)}"
            f"&to={quote_plus(to_address)}"
            "&ref=YumPosBot"
            "&appmetrica_tracking_id=1178268795219780156"
        )

    return link


if __name__ == "__main__":
    print(geocode_osm('Бишкек vefa'))
