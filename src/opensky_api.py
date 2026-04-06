import json
import logging
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .base_api import BaseAPI


class OpenSkyAPI(BaseAPI):
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
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.propagate = False

    def _get_json(self, url: str, params: dict):
        query = urlencode(params)
        full_url = f"{url}?{query}" if query else url
        self.logger.info("GET %s", full_url)
        request = Request(full_url, headers=self.headers)
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))

    def get_bounding_box(self, cuntry_name):
        """Берём коордитнаты из апи Nominatim нужной страны
        на выходе максимальная и минимальная широта, долгота"""

        url = self.nominatim_url
        params = {
            "q": cuntry_name,
            "format": "json",
            "limit": 1,
        }

        data = self._get_json(url, params)
        if data:
            bbox = data[0]["boundingbox"]
            self.logger.info("Bounding box found for country=%s", cuntry_name)
            return {
                "lamin": float(bbox[0]),
                "lamax": float(bbox[1]),
                "lomin": float(bbox[2]),
                "lomax": float(bbox[3]),
            }
        self.logger.warning("Country not found in Nominatim: %s", cuntry_name)
        return None

    def get_aircraft(self, bbox):
        """с помощью известных координат
        в заданом квадрате ищем все рейсы"""
        if not bbox:
            return []
        params = {
            "lamin": bbox["lamin"],
            "lamax": bbox["lamax"],
            "lomin": bbox["lomin"],
            "lomax": bbox["lomax"],
        }
        data = self._get_json(self.opensky_url, params)
        fly_data = data.get("states", [])
        len_fly = len(fly_data)
        self.logger.info("Fetched aircraft count=%s", len_fly)
        return {
            "fly_data": fly_data,
            "count": len_fly,
        }

    def get_aircraft_by_country(self, country_name: str):
        try:
            self.logger.info("Request aircraft by country=%s", country_name)
            bbox = self.get_bounding_box(country_name)
            if not bbox:
                self.logger.warning("Country not found: %s", country_name)
                return {"fly_data": [], "count": 0, "error": "Страна не найдена"}
            return self.get_aircraft(bbox)
        except HTTPError as error:
            self.logger.error("HTTP error from API: code=%s", error.code)
            return {
                "fly_data": [],
                "count": 0,
                "error": f"Ошибка HTTP при запросе к API: {error.code}",
            }
        except URLError:
            self.logger.error("Network error while requesting API")
            return {
                "fly_data": [],
                "count": 0,
                "error": "Сетевая ошибка: нет доступа к API",
            }
        except TimeoutError:
            self.logger.error("Timeout while requesting API")
            return {
                "fly_data": [],
                "count": 0,
                "error": "Сетевая ошибка: превышено время ожидания API",
            }
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON in API response")
            return {
                "fly_data": [],
                "count": 0,
                "error": "Ошибка данных: API вернул некорректный JSON",
            }

    def get_logs(self, limit: int = 30) -> list[str]:
        if not self.log_path.exists():
            return []
        with self.log_path.open("r", encoding="utf-8") as log_file:
            lines = [line.rstrip("\n") for line in log_file]
        return lines[-limit:]

    def clear_logs(self) -> None:
        self.log_path.write_text("", encoding="utf-8")


if __name__ == "__main__":
    api = OpenSkyAPI()
    data = api.get_aircraft_by_country("Russia")
    print(data["count"])
