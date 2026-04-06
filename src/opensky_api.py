# OpenSkyAPI + Nominati

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from .base_api import BaseAPI


class OpenSkyAPI(BaseAPI):
    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.opensky_url = "https://opensky-network.org/api/states/all"
        self.headers = {"User-Agent": "MyAircraftApp/1.0"}

    def _get_json(self, url: str, params: dict):
        query = urlencode(params)
        full_url = f"{url}?{query}" if query else url
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
            return {
                "lamin": float(bbox[0]),
                "lamax": float(bbox[1]),
                "lomin": float(bbox[2]),
                "lomax": float(bbox[3]),
            }
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
        return {
            "fly_data": fly_data,
            "count": len_fly,
        }

    def get_aircraft_by_country(self, country_name: str):
        try:
            bbox = self.get_bounding_box(country_name)
            if not bbox:
                return {"fly_data": [], "count": 0, "error": "Страна не найдена"}
            return self.get_aircraft(bbox)
        except HTTPError as error:
            return {
                "fly_data": [],
                "count": 0,
                "error": f"Ошибка HTTP при запросе к API: {error.code}",
            }
        except URLError:
            return {
                "fly_data": [],
                "count": 0,
                "error": "Сетевая ошибка: нет доступа к API",
            }
        except TimeoutError:
            return {
                "fly_data": [],
                "count": 0,
                "error": "Сетевая ошибка: превышено время ожидания API",
            }
        except json.JSONDecodeError:
            return {
                "fly_data": [],
                "count": 0,
                "error": "Ошибка данных: API вернул некорректный JSON",
            }


if __name__ == "__main__":
    api = OpenSkyAPI()
    data = api.get_aircraft_by_country("Russia")
    print(data["count"])
