# OpenSkyAPI + Nominati

import requests, json
from .base_api import BaseAPI


class OpenSkyAPI(BaseAPI):
    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.opensky_url = "https://opensky-network.org/api/states/all"
        self.headers = {"User-Agent": "MyAircraftApp/1.0"}

    def get_bounding_box(self, cuntry_name):
        """Берём коордитнаты из апи Nominatim нужной страны
        на выходе максимальная и минимальная широта, долгота"""

        url = self.nominatim_url
        params = {
            "q": cuntry_name,
            "format": "json",
            "limit": 1,
        }

        response = requests.get(url, params=params, headers=self.headers)
        data = response.json()
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
        response = requests.get(self.opensky_url, params=params)
        if response.status_code == 200:
            fly_data = response.json().get("states", [])
            len_fly = len(fly_data)
            return {
                "fly_data": fly_data,
                "count": len_fly,
            }  # словарь с понятными ключами
        return {"fly_data": [], "count": 0}

    def get_aircraft_by_country(self, country_name: str):
        bbox = self.get_bounding_box(country_name)
        if not bbox:
            return {"fly_data": [], "count": 0, "error": "Страна не найдена"}
        return self.get_aircraft(bbox)


if __name__ == "__main__":
    api = OpenSkyAPI()
    data = api.get_aircraft_by_country("Russia")
    print(data["count"])
