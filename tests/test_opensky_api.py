import json
import logging
from urllib.error import HTTPError, URLError

from src.opensky_api import OpenSkyAPI


def test_get_bounding_box_returns_float_coordinates(monkeypatch):
    api = OpenSkyAPI()

    def fake_get_json(url, params):
        assert params["q"] == "Spain"
        return [{"boundingbox": ["10.0", "20.0", "30.0", "40.0"]}]

    monkeypatch.setattr(api, "_get_json", fake_get_json)

    bbox = api.get_bounding_box("Spain")

    assert bbox == {"lamin": 10.0, "lamax": 20.0, "lomin": 30.0, "lomax": 40.0}


def test_get_bounding_box_returns_none_for_empty_response(monkeypatch):
    api = OpenSkyAPI()
    monkeypatch.setattr(api, "_get_json", lambda *_: [])

    assert api.get_bounding_box("Unknown") is None


def test_get_aircraft_returns_empty_list_for_empty_bbox():
    api = OpenSkyAPI()

    assert api.get_aircraft(None) == []


def test_get_aircraft_maps_states_to_count(monkeypatch):
    api = OpenSkyAPI()
    bbox = {"lamin": 1.0, "lamax": 2.0, "lomin": 3.0, "lomax": 4.0}

    def fake_get_json(url, params):
        assert params == bbox
        return {"states": [["a"], ["b"], ["c"]]}

    monkeypatch.setattr(api, "_get_json", fake_get_json)

    result = api.get_aircraft(bbox)

    assert result["count"] == 3
    assert len(result["fly_data"]) == 3


def test_get_aircraft_by_country_returns_not_found_when_bbox_absent(monkeypatch):
    api = OpenSkyAPI()
    monkeypatch.setattr(api, "get_bounding_box", lambda *_: None)

    result = api.get_aircraft_by_country("Atlantis")

    assert result["count"] == 0
    assert "Страна не найдена" in result["error"]


def test_get_aircraft_by_country_returns_http_error_message(monkeypatch):
    api = OpenSkyAPI()

    def raise_http_error(*_):
        raise HTTPError(
            url="http://x", code=503, msg="Service Unavailable", hdrs=None, fp=None
        )

    monkeypatch.setattr(api, "get_bounding_box", raise_http_error)
    result = api.get_aircraft_by_country("Spain")
    assert "503" in result["error"]


def test_get_aircraft_by_country_returns_network_error_message(monkeypatch):
    api = OpenSkyAPI()
    monkeypatch.setattr(
        api, "get_bounding_box", lambda *_: (_ for _ in ()).throw(URLError("offline"))
    )

    result = api.get_aircraft_by_country("Spain")
    assert "Сетевая ошибка" in result["error"]


def test_get_aircraft_by_country_returns_timeout_error_message(monkeypatch):
    api = OpenSkyAPI()
    monkeypatch.setattr(
        api, "get_bounding_box", lambda *_: (_ for _ in ()).throw(TimeoutError())
    )

    result = api.get_aircraft_by_country("Spain")
    assert "превышено время ожидания" in result["error"]


def test_get_aircraft_by_country_returns_json_error_message(monkeypatch):
    api = OpenSkyAPI()
    monkeypatch.setattr(
        api,
        "get_bounding_box",
        lambda *_: (_ for _ in ()).throw(json.JSONDecodeError("bad", "doc", 0)),
    )

    result = api.get_aircraft_by_country("Spain")
    assert "некорректный JSON" in result["error"]


def test_get_logs_and_clear_logs(tmp_path):
    api = OpenSkyAPI()
    api.log_path = tmp_path / "opensky_api.log"
    handler = logging.FileHandler(api.log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    api.logger.handlers = [handler]
    api.logger.propagate = False
    api.logger.info("line1")
    api.logger.info("line2")
    handler.flush()

    logs = api.get_logs(limit=1)
    assert logs == ["line2"]

    api.clear_logs()
    assert api.get_logs() == []
