# абстрактный BaseAPI
from abc import ABC, abstractmethod


class BaseAPI(ABC):
    @abstractmethod
    def get_bounding_box(self, country_name):
        """Получаем координаты страны (min_lat, max_lat, min_lon, max_lon)"""

    pass

    @abstractmethod
    def get_aircraft(self, bbox):
        """Получаем списки самолётов нужном квадрате"""
        pass
