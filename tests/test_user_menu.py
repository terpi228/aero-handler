from pathlib import Path

from src import user_interface as ui


def _state(callsign="A1", country="Spain", baro=1000.0, geo=None):
    row = [None] * 14
    row[0] = "icao"
    row[1] = callsign
    row[2] = country
    row[7] = baro
    row[13] = geo
    return row


class DummyAPI:
    def __init__(self, payload):
        self.payload = payload
        self.logs = ["2026-04-07 10:00:00 | INFO | test log"]
        self.clear_logs_called = False

    def get_aircraft_by_country(self, _country):
        return self.payload

    def get_logs(self, limit=30):
        return self.logs[-limit:]

    def clear_logs(self):
        self.logs = []
        self.clear_logs_called = True


class DummySaver:
    def __init__(self):
        self.history = []
        self.clear_called = False

    def append_top(self, top, top_count, country_name):
        self.history.append(
            {
                "request_number": len(self.history) + 1,
                "country": country_name,
                "top_count": top_count,
                "top": top,
            }
        )
        return Path("data/latest.json")

    def load(self, _file_name="latest.json"):
        return {"requests": self.history}

    def clear_history(self):
        self.history = []
        self.clear_called = True
        return Path("data/latest.json")


def test_user_menu_stops_on_api_error(monkeypatch, capsys):
    monkeypatch.setattr(
        ui,
        "OpenSkyAPI",
        lambda: DummyAPI({"error": "boom", "count": 0, "fly_data": []}),
    )
    monkeypatch.setattr(ui, "JSONSaver", lambda: DummySaver())
    inputs = iter(["Spain"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    ui.user_menu()
    out = capsys.readouterr().out

    assert "Не удалось получить данные" in out


def test_user_menu_handles_menu_actions(monkeypatch, capsys):
    payload = {
        "count": 3,
        "fly_data": [
            _state("A1", "Spain", 1000.0, None),
            _state("A2", "France", 2000.0, 2500.0),
            _state("A3", "Spain", 3000.0, None),
        ],
    }
    saver = DummySaver()

    monkeypatch.setattr(ui, "OpenSkyAPI", lambda: DummyAPI(payload))
    monkeypatch.setattr(ui, "JSONSaver", lambda: saver)

    inputs = iter(
        [
            "Spain",  # country
            "2",  # initial top_n
            "2",  # menu: by registration country
            "Spain",  # registration country
            "",  # pause
            "3",  # menu: altitude range
            "1000",  # min
            "3000",  # max
            "",  # pause
            "5",  # menu: history
            "",  # pause
            "6",  # menu: clear history
            "",  # pause
            "7",  # menu: show api logs
            "",  # pause
            "8",  # menu: clear api logs
            "",  # pause
            "0",  # exit
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    ui.user_menu()
    out = capsys.readouterr().out

    assert "получено 3 самолетов" in out
    assert "Самолёты с регистрацией в стране Spain" in out
    assert "Самолёты в диапазоне высот 1000.0..3000.0 м:" in out
    assert "Последние запросы топов:" in out
    assert "История топов очищена." in out
    assert "Последние логи OpenSky API:" in out
    assert "Логи API очищены." in out
    assert saver.clear_called is True


def test_user_menu_handles_invalid_menu_input(monkeypatch, capsys):
    payload = {"count": 1, "fly_data": [_state("A1", "Spain", 1000.0, None)]}
    monkeypatch.setattr(ui, "OpenSkyAPI", lambda: DummyAPI(payload))
    monkeypatch.setattr(ui, "JSONSaver", lambda: DummySaver())

    inputs = iter(
        [
            "Spain",
            "1",
            "9",  # invalid menu item
            "",  # pause
            "0",
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    ui.user_menu()
    out = capsys.readouterr().out
    assert "Неизвестный пункт меню. Введите число от 0 до 8." in out


def test_user_menu_rejects_invalid_top_n_at_start(monkeypatch, capsys):
    payload = {"count": 1, "fly_data": [_state()]}
    monkeypatch.setattr(ui, "OpenSkyAPI", lambda: DummyAPI(payload))
    monkeypatch.setattr(ui, "JSONSaver", lambda: DummySaver())
    inputs = iter(["Spain", "0"])
    monkeypatch.setattr("builtins.input", lambda _="": next(inputs))

    ui.user_menu()
    out = capsys.readouterr().out
    assert "Количество топов должно быть больше 0." in out
