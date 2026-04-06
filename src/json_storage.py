import json
from datetime import datetime
from pathlib import Path
from typing import Any


class JSONSaver:
    """Сохранение данных в JSON-файлы."""

    def __init__(self, base_dir: str = "data") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, data: Any, file_name: str) -> Path:
        """Сохраняет данные в указанный JSON-файл."""
        normalized_name = file_name if file_name.endswith(".json") else f"{file_name}.json"
        file_path = self.base_dir / normalized_name
        with file_path.open("w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=2)
        return file_path

    def load(self, file_name: str = "latest.json") -> Any:
        """Загружает данные из JSON-файла."""
        normalized_name = file_name if file_name.endswith(".json") else f"{file_name}.json"
        file_path = self.base_dir / normalized_name
        with file_path.open("r", encoding="utf-8") as json_file:
            return json.load(json_file)

    def append_top(self, top: list[dict[str, Any]], top_count: int, country_name: str) -> Path:
        """Добавляет запись топа в единый latest.json с номером запроса."""
        file_path = self.base_dir / "latest.json"
        if file_path.exists():
            try:
                payload = self.load("latest.json")
            except (json.JSONDecodeError, OSError):
                payload = {"requests": []}
        else:
            payload = {"requests": []}

        requests = payload.get("requests", [])
        request_number = len(requests) + 1
        requests.append(
            {
                "request_number": request_number,
                "country": country_name,
                "top_count": top_count,
                "top": top,
                "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
        payload["requests"] = requests[-50:]
        return self.save(payload, "latest.json")

    def clear_history(self) -> Path:
        """Очищает историю топов в latest.json."""
        return self.save({"requests": []}, "latest.json")
