from src.user_interface import (
    _altitude_key,
    _ask_top_n,
    _build_compact_top,
    _filter_by_altitude_range,
    _filter_by_registration_country,
    _to_compact_aircraft,
)


def _make_state(callsign, country, baro_altitude, geo_altitude):
    state = [None] * 14
    state[0] = "icao"
    state[1] = callsign
    state[2] = country
    state[7] = baro_altitude
    state[13] = geo_altitude
    return state


def test_altitude_key_prefers_geo_altitude():
    state = _make_state("AB123", "Spain", 9000.0, 10000.0)

    assert _altitude_key(state) == 10000.0


def test_to_compact_aircraft_uses_fallback_altitude_and_strips_callsign():
    state = _make_state("  AB123  ", "Spain", 9100.0, None)

    compact = _to_compact_aircraft(state)

    assert compact["callsign"] == "AB123"
    assert compact["origin_country"] == "Spain"
    assert compact["altitude_m"] == 9100.0


def test_build_compact_top_returns_sorted_by_altitude_desc():
    low = _make_state("LOW1", "Spain", 3000.0, None)
    high = _make_state("HIGH1", "Spain", 3000.0, 12000.0)
    mid = _make_state("MID1", "Spain", 8000.0, None)
    data = {"fly_data": [low, high, mid]}

    top = _build_compact_top(data, 2)

    assert [item["callsign"] for item in top] == ["HIGH1", "MID1"]


def test_filter_by_registration_country_is_case_insensitive():
    data = {
        "fly_data": [
            _make_state("A1", "Spain", 3000.0, None),
            _make_state("A2", "France", 5000.0, None),
            _make_state("A3", "spain", 7000.0, None),
        ]
    }

    filtered = _filter_by_registration_country(data, "  SPAIN ")

    assert [item["callsign"] for item in filtered] == ["A1", "A3"]


def test_filter_by_altitude_range_includes_bounds():
    data = {
        "fly_data": [
            _make_state("A1", "Spain", 1000.0, None),
            _make_state("A2", "Spain", 2000.0, None),
            _make_state("A3", "Spain", 3000.0, None),
        ]
    }

    filtered = _filter_by_altitude_range(data, 1000.0, 2000.0)

    assert [item["callsign"] for item in filtered] == ["A1", "A2"]


def test_ask_top_n_invalid_integer(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "abc")

    result = _ask_top_n()
    printed = capsys.readouterr().out

    assert result is None
    assert "целое число" in printed


def test_ask_top_n_caps_large_value(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "150")

    assert _ask_top_n() == 100
