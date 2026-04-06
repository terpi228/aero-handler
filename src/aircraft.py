class Aircraft:
    def __init__(
        self, callsign: str, registration_country: str, velocity: float, altitude: float
    ):
        # Валидация
        if not callsign or not callsign.strip():
            raise ValueError("Позывной не может быть пустым")
        if not registration_country or not registration_country.strip():
            raise ValueError("Страна регистрации не может быть пустой")
        if velocity < 0:
            raise ValueError(f"Скорость не может быть отрицательной: {velocity}")
        if altitude < 0:
            raise ValueError(f"Высота не может быть отрицательной: {altitude}")

        # Присвоение атрибутам
        self._callsign = callsign.strip()
        self._registration_country = registration_country.strip()
        self._velocity = velocity
        self._altitude = altitude

    # Геттеры (опционально)
    @property
    def callsign(self):
        return self._callsign

    @property
    def registration_country(self):
        return self._registration_country

    @property
    def velocity(self):
        return self._velocity

    @property
    def altitude(self):
        return self._altitude

    @staticmethod
    def cast_to_object_list(states: list) -> list:
        aircraft_list = []
        for state in states:
            # Извлекаем данные из state
            callsign = state[1].strip() if state[1] else "N/A"
            country = state[2].strip() if state[2] else "Unknown"
            velocity = float(state[9]) if state[9] is not None else 0.0
            altitude = float(state[7]) if state[7] is not None else 0.0

            try:
                aircraft = Aircraft(callsign, country, velocity, altitude)
                aircraft_list.append(aircraft)
            except ValueError as e:
                # Логируем ошибку (например, при отрицательной скорости)
                print(f"Пропущен самолёт {callsign}: {e}")
                continue
        return aircraft_list


if __name__ == "__main__":
    pass
