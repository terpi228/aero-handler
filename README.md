# ✈️ Aero Handler

Консольное Python-приложение для получения и анализа данных о самолётах над выбранной страной.
Использует внешние API:
- [Nominatim](https://nominatim.openstreetmap.org/) для координат страны (bounding box)
- [OpenSky Network](https://opensky-network.org/) для state-vector самолётов

## Что умеет

- запрашивает страну и получает список самолётов в её воздушном пространстве
- показывает общее количество найденных рейсов
- строит топ `N` самолётов по высоте
- фильтрует самолёты:
  - по стране регистрации
  - по диапазону высот
- сохраняет историю запросов в `data/latest.json`
- показывает последние запросы и умеет очищать историю

## Технологии

- Python 3.14+
- `requests` (зависимость проекта)
- `pytest`, `pytest-cov` (тесты и покрытие)

## Быстрый старт

```bash
git clone <url-репозитория>
cd aero-handler
python -m pip install requests pytest pytest-cov black isort flake8
```

Запуск приложения:

```bash
python main.py
```

## Команды для разработки

### Всё разом (красивый вывод в консоль)

Один прогон: `isort` → `black` → `flake8` → `pytest`, с понятными сообщениями вида «в параметре … всё ок».

```bash
python scripts/dev_check.py
```

Только проверка без автоправок (как в CI):

```bash
python scripts/dev_check.py --ci
```

С дополнительным шагом покрытия:

```bash
python scripts/dev_check.py --cov
```

Если установлен `make` (Git Bash, WSL, Linux, macOS):

```bash
make check
make check-ci
make check-cov
```

### По отдельности

Запуск тестов:

```bash
python -m pytest -q
```

Проверка покрытия:

```bash
python -m pytest --cov=src --cov-report=term -q
```

## Текущее качество

- автотесты: **33 passed**
- общее покрытие: **85%**

Покрытие ключевых модулей:
- `src/aircraft.py` — 98%
- `src/json_storage.py` — 100%
- `src/opensky_api.py` — 82%
- `src/user_interface.py` — 80%

## Структура проекта

```text
aero-handler/
├── main.py
├── src/
│   ├── aircraft.py
│   ├── base_api.py
│   ├── base_storage.py
│   ├── json_storage.py
│   ├── opensky_api.py
│   └── user_interface.py
├── tests/
│   ├── test_aircraft.py
│   ├── test_json_storage.py
│   ├── test_opensky_api.py
│   ├── test_user_interface.py
│   ├── test_user_menu.py
│   └── test_abstract_contracts.py
└── data/
    └── latest.json
```

## Пример сценария в консоли

```text
введите название страны:Spain
получено 123 самолетов из странны Spain.
Введите количество самолетов в топе в мире: 10
Текущий топ по высоте:
1. callsign=...
...
```

## Архитектура

- `BaseAPI` и `BaseStorage` задают абстрактные контракты
- `OpenSkyAPI` инкапсулирует сетевое взаимодействие и обработку ошибок API
- `Aircraft` валидирует входные данные и хранит модель самолёта
- `JSONSaver` отвечает только за работу с JSON-хранилищем
- `user_interface` содержит пользовательский сценарий и меню