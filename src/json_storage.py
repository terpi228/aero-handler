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
        file_path = self.base_dir / file_name
        with file_path.open("w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=2)
        return file_path

    def save_snapshot(self, country_name: str, data: Any) -> Path:
        """
        Автоматически сохраняет снимок данных:
        - в уникальный файл с временем;
        - в latest.json (последний результат).
        """
        safe_country = country_name.strip().replace(" ", "_").lower() or "unknown"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_name = f"{safe_country}_{timestamp}.json"

        snapshot_path = self.save(data, snapshot_name)
        self.save(data, "latest.json")
        return snapshot_path
