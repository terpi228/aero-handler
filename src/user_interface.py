# функция user_interaction()
from src.json_storage import JSONSaver
from src.opensky_api import OpenSkyAPI


def _altitude_key(state: list) -> float:
    """Ключ сортировки по высоте (geo_altitude с fallback на baro_altitude)."""
    geo_altitude = state[13] if len(state) > 13 else None
    baro_altitude = state[7] if len(state) > 7 else None
    altitude = geo_altitude if geo_altitude is not None else baro_altitude
    return float(altitude) if altitude is not None else -1.0


def _to_compact_aircraft(state: list) -> dict:
    """Преобразует state-vector OpenSky в компактную запись для JSON."""
    icao24 = state[0] if len(state) > 0 else None
    callsign = state[1].strip() if len(state) > 1 and state[1] else None
    origin_country = state[2] if len(state) > 2 else None
    geo_altitude = state[13] if len(state) > 13 else None
    baro_altitude = state[7] if len(state) > 7 else None
    altitude = geo_altitude if geo_altitude is not None else baro_altitude
    return {
        "icao24": icao24,
        "callsign": callsign,
        "origin_country": origin_country,
        "altitude_m": altitude,
    }


def _ask_top_n() -> int | None:
    try:
        top_n = int(input("Введите количество самолетов в топе в мире: "))
    except ValueError:
        print("Нужно ввести целое число.")
        return None

    if top_n <= 0:
        print("Количество топов должно быть больше 0.")
        return None
    if top_n > 100:
        print("Слишком большой топ. Установлен лимит 100.")
        return 100
    return top_n


def _build_compact_top(data: dict, top_n: int) -> list[dict]:
    fly_data = data.get("fly_data", [])
    sorted_by_altitude = sorted(fly_data, key=_altitude_key, reverse=True)
    top_list = sorted_by_altitude[:top_n]
    return [_to_compact_aircraft(item) for item in top_list]


def _print_compact_top(compact_top: list[dict]) -> None:
    if not compact_top:
        print("Нет данных для топа.")
        return
    print("Текущий топ по высоте:")
    for idx, item in enumerate(compact_top, start=1):
        print(
            f"{idx}. callsign={item.get('callsign')}, "
            f"altitude_m={item.get('altitude_m')}, "
            f"country={item.get('origin_country')}"
        )


def _filter_by_registration_country(
    data: dict, registration_country: str
) -> list[dict]:
    target = registration_country.strip().lower()
    if not target:
        return []
    fly_data = data.get("fly_data", [])
    compact = [_to_compact_aircraft(item) for item in fly_data]
    return [
        item
        for item in compact
        if (item.get("origin_country") or "").strip().lower() == target
    ]


def _filter_by_altitude_range(
    data: dict, min_altitude: float, max_altitude: float
) -> list[dict]:
    fly_data = data.get("fly_data", [])
    compact = [_to_compact_aircraft(item) for item in fly_data]
    return [
        item
        for item in compact
        if item.get("altitude_m") is not None
        and min_altitude <= float(item["altitude_m"]) <= max_altitude
    ]


def _print_aircraft_list(
    title: str, aircraft_list: list[dict], limit: int = 20
) -> None:
    if not aircraft_list:
        print("Ничего не найдено.")
        return
    print(title)
    for idx, item in enumerate(aircraft_list[:limit], start=1):
        print(
            f"{idx}. callsign={item.get('callsign')}, "
            f"altitude_m={item.get('altitude_m')}, "
            f"country={item.get('origin_country')}"
        )
    if len(aircraft_list) > limit:
        print(f"... и ещё {len(aircraft_list) - limit} записей")


def _pause() -> None:
    input("\nНажмите Enter, чтобы вернуться в меню...")


def _print_api_logs(api: OpenSkyAPI, limit: int = 20) -> None:
    logs = api.get_logs(limit=limit)
    if not logs:
        print("Логи API пока пусты.")
        return
    print("Последние логи OpenSky API:")
    for line in logs:
        print(f"- {line}")


def user_menu():
    name_cuntry = input(str("введите название страны:"))
    api = OpenSkyAPI()
    saver = JSONSaver()
    data = api.get_aircraft_by_country(name_cuntry)

    if "error" in data:
        print(f"Не удалось получить данные: {data['error']}")
        return

    print(f"получено {data['count']} самолетов из странны {name_cuntry}.")

    top_n = _ask_top_n()
    if top_n is None:
        return

    compact_top = _build_compact_top(data, top_n)
    saved_path = saver.append_top(
        top=compact_top,
        top_count=len(compact_top),
        country_name=name_cuntry,
    )
    _print_compact_top(compact_top)
    print(f"Топ {len(compact_top)} сохранён в один файл: {saved_path}")

    while True:
        print("""
-------------menu--------------
Основное:
1. Пересчитать топ N по высоте
2. Самолёты по стране регистрации
3. Фильтр по диапазону высот

История:
5. История топов
6. Очистить историю топов

Логи API:
7. Показать логи API
8. Очистить логи API

0. Выход
Выберите действие (0-8):
""")

        users_input = input("Введите действие:").strip()
        if users_input == "1":
            top_n = _ask_top_n()
            if top_n is None:
                _pause()
                continue

            compact_top = _build_compact_top(data, top_n)
            saved_path = saver.append_top(
                top=compact_top,
                top_count=len(compact_top),
                country_name=name_cuntry,
            )
            _print_compact_top(compact_top)
            print(f"Топ {len(compact_top)} сохранён в один файл: {saved_path}")
            _pause()
        elif users_input == "2":
            registration_country = input("Введите страну регистрации: ").strip()
            result = _filter_by_registration_country(data, registration_country)
            _print_aircraft_list(
                f"Самолёты с регистрацией в стране {registration_country}:",
                result,
            )
            _pause()
        elif users_input == "3":
            try:
                min_altitude = float(input("Введите минимальную высоту (м): ").strip())
                max_altitude = float(input("Введите максимальную высоту (м): ").strip())
            except ValueError:
                print("Нужно ввести числа для диапазона высот.")
                _pause()
                continue
            if min_altitude > max_altitude:
                print("Минимальная высота не может быть больше максимальной.")
                _pause()
                continue
            result = _filter_by_altitude_range(data, min_altitude, max_altitude)
            _print_aircraft_list(
                f"Самолёты в диапазоне высот {min_altitude}..{max_altitude} м:",
                result,
            )
            _pause()
        elif users_input == "5":
            try:
                history = saver.load("latest.json").get("requests", [])
            except FileNotFoundError, OSError, ValueError:
                history = []

            if not history:
                print("История топов пока пуста.")
                _pause()
                continue

            print("Последние запросы топов:")
            for item in history[-5:]:
                print(
                    f"- Запрос #{item.get('request_number')}: "
                    f"страна={item.get('country')}, "
                    f"top_count={item.get('top_count')}"
                )
            _pause()
        elif users_input == "6":
            saver.clear_history()
            print("История топов очищена.")
            _pause()
        elif users_input == "7":
            _print_api_logs(api)
            _pause()
        elif users_input == "8":
            api.clear_logs()
            print("Логи API очищены.")
            _pause()
        elif users_input == "0":
            print("Выход из программы.")
            break
        else:
            print("Неизвестный пункт меню. Введите число от 0 до 8.")
            _pause()
