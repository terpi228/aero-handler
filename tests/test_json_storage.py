import json

from src.json_storage import JSONSaver


def test_save_adds_json_extension_and_load_reads_data(tmp_path):
    saver = JSONSaver(base_dir=str(tmp_path))
    payload = {"a": 1, "b": [1, 2, 3]}

    path = saver.save(payload, "sample")

    assert path.name == "sample.json"
    assert saver.load("sample") == payload


def test_append_top_creates_incrementing_request_number(tmp_path):
    saver = JSONSaver(base_dir=str(tmp_path))

    saver.append_top(top=[{"callsign": "A"}], top_count=1, country_name="Spain")
    saver.append_top(top=[{"callsign": "B"}], top_count=1, country_name="France")

    history = saver.load("latest.json")["requests"]
    assert len(history) == 2
    assert history[0]["request_number"] == 1
    assert history[1]["request_number"] == 2
    assert history[1]["country"] == "France"


def test_append_top_recovers_from_invalid_latest_json(tmp_path):
    saver = JSONSaver(base_dir=str(tmp_path))
    broken_file = tmp_path / "latest.json"
    broken_file.write_text("{broken-json", encoding="utf-8")

    saver.append_top(top=[{"callsign": "X"}], top_count=1, country_name="Italy")

    loaded = json.loads(broken_file.read_text(encoding="utf-8"))
    assert len(loaded["requests"]) == 1
    assert loaded["requests"][0]["request_number"] == 1


def test_clear_history_overwrites_latest_with_empty_requests(tmp_path):
    saver = JSONSaver(base_dir=str(tmp_path))
    saver.append_top(top=[{"callsign": "A"}], top_count=1, country_name="Spain")

    saver.clear_history()
    loaded = saver.load("latest.json")

    assert loaded == {"requests": []}
