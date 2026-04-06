from abc import ABC, abstractmethod


class BaseStorage(ABC):
    @abstractmethod
    def add_aircraft(self, aircraft) -> None:
        """Добавляет объект Aircraft в хранилище."""
        pass

    @abstractmethod
    def get_aircraft(self, criteria: dict) -> list:
        """Возвращает список объектов Aircraft, удовлетворяющих критериям.
        criteria: словарь с полями для фильтрации, например:
                  {'registration_country': 'Spain'} или
                  {'altitude_min': 1000, 'altitude_max': 5000}
        """
        pass

    @abstractmethod
    def delete_aircraft(self, aircraft) -> None:
        """Удаляет объект Aircraft из хранилища."""
        pass
