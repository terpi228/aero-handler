# api_client.py
import requests
import logging
from pathlib import Path

class OpenSkyAPI:
    """
    Клиент для работы с OpenSky Network API и Nominatim.
    """

    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.opensky_url = "https://opensky-network.org/api/states/all"
        self.headers = {"User-Agent": "MyAircraftApp/1.0"}
        self.log_path = Path("data/opensky_api.log")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("opensky_api")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.FileHandler(self.log_path, encoding="utf-8")
            formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s",
                                          datefmt="%Y-%m-%d %H:%M:%S")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.propagate = False

    def _get_json(self, url, params=None):
        """Выполняет GET-запрос и возвращает JSON."""
        response = requests.get(url, params=params, headers=self.headers, timeout=20)
        response.raise_for_status()
        return response.json()

    def get_bounding_box(self, country_name):
        """
        Получает ограничивающий прямоугольник страны через Nominatim.
        Возвращает словарь с ключами lamin, lamax, lomin, lomax или None.
        """
        self.logger.info("Requesting bounding box for %s", country_name)
        params = {"q": country_name, "format": "json", "limit": 1}
        try:
            data = self._get_json(self.nominatim_url, params)
            if data:
                bbox = data[0]["boundingbox"]
                self.logger.info("Bounding box found for %s", country_name)
                return {
                    "lamin": float(bbox[0]),
                    "lamax": float(bbox[1]),
                    "lomin": float(bbox[2]),
                    "lomax": float(bbox[3]),
                }
            else:
                self.logger.warning("Country not found: %s", country_name)
                return None
        except requests.exceptions.RequestException as e:
            self.logger.error("Error fetching bounding box: %s", e)
            return None

    def get_aircraft(self, bbox):
        """
        Получает список самолётов в указанном прямоугольнике через OpenSky API.
        Возвращает список states (массивов).
        """
        if not bbox:
            return []
        params = {
            "lamin": bbox["lamin"],
            "lamax": bbox["lamax"],
            "lomin": bbox["lomin"],
            "lomax": bbox["lomax"],
        }
        try:
            data = self._get_json(self.opensky_url, params)
            states = data.get("states", [])
            self.logger.info("Fetched %d aircraft", len(states))
            return states
        except requests.exceptions.RequestException as e:
            self.logger.error("Error fetching aircraft: %s", e)
            return []

    def get_aircraft_by_country(self, country_name):
        """Удобный метод: получает bbox страны и затем самолёты."""
        bbox = self.get_bounding_box(country_name)
        if not bbox:
            return []
        return self.get_aircraft(bbox)