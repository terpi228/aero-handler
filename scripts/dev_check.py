#!/usr/bin/env python3
"""Одна команда: формат, линт, тесты — с человекочитаемым выводом."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _banner(title: str) -> None:
    line = "=" * 62
    print()
    print(line)
    print(f"  {title}")
    print(line)


def _ok(param: str, detail: str = "всё супер на 100%.") -> None:
    print(f"  В параметре «{param}» — всё ок; {detail}")


def _fail(param: str, hint: str = "смотри вывод команды выше.") -> None:
    print(f"  В параметре «{param}» — есть замечания; {hint}")


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=True,
    )


def _parse_coverage_percent(text: str) -> str | None:
    for line in text.splitlines():
        if line.strip().startswith("TOTAL"):
            parts = line.split()
            if len(parts) >= 4 and parts[-1].endswith("%"):
                return parts[-1]
    match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", text)
    if match:
        return f"{match.group(1)}%"
    return None


def main() -> int:
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except AttributeError, OSError, ValueError:
            pass

    parser = argparse.ArgumentParser(description="Проверка проекта с красивым выводом.")
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Только проверка без правок (isort/black --check).",
    )
    parser.add_argument(
        "--cov",
        action="store_true",
        help="Добавить шаг с покрытием кода (pytest-cov).",
    )
    args = parser.parse_args()
    cwd = ROOT
    failed = False

    _banner("Шаг 1 · сортировка импортов (isort)")
    if args.ci:
        r = _run([sys.executable, "-m", "isort", "--check-only", "."], cwd)
    else:
        r = _run([sys.executable, "-m", "isort", "."], cwd)
    if r.stdout:
        print(r.stdout.rstrip())
    if r.stderr:
        print(r.stderr.rstrip())
    if r.returncode == 0:
        _ok("импорты", "порядок на 100%.")
    else:
        _fail("импорты")
        failed = True

    _banner("Шаг 2 · форматирование (black)")
    if args.ci:
        r = _run([sys.executable, "-m", "black", "--check", "."], cwd)
    else:
        r = _run([sys.executable, "-m", "black", "."], cwd)
    if r.stdout:
        print(r.stdout.rstrip())
    if r.stderr:
        print(r.stderr.rstrip())
    if r.returncode == 0:
        _ok("стиль кода", "black доволен, всё ровно.")
    else:
        _fail("стиль кода")
        failed = True

    _banner("Шаг 3 · линтер (flake8)")
    r = _run([sys.executable, "-m", "flake8", "."], cwd)
    if r.stdout:
        print(r.stdout.rstrip())
    if r.stderr:
        print(r.stderr.rstrip())
    if r.returncode == 0:
        _ok("flake8", "замечаний нет.")
    else:
        _fail("flake8")
        failed = True

    _banner("Шаг 4 · тесты (pytest)")
    r = _run([sys.executable, "-m", "pytest", "-q"], cwd)
    if r.stdout:
        print(r.stdout.rstrip())
    if r.stderr:
        print(r.stderr.rstrip())
    if r.returncode == 0:
        _ok("тесты", "все зелёные, можно в прод (шутка — в ревью).")
    else:
        _fail("тесты")
        failed = True

    if args.cov:
        _banner("Шаг 5 · покрытие (pytest-cov)")
        r = _run(
            [
                sys.executable,
                "-m",
                "pytest",
                "--cov=src",
                "--cov-report=term",
                "-q",
            ],
            cwd,
        )
        combined = (r.stdout or "") + "\n" + (r.stderr or "")
        if r.stdout:
            print(r.stdout.rstrip())
        if r.stderr:
            print(r.stderr.rstrip())
        pct = _parse_coverage_percent(combined)
        if r.returncode == 0:
            if pct:
                _ok("покрытие", f"отчёт готов, суммарно {pct} — отличный уровень.")
            else:
                _ok("покрытие", "отчёт готов, метрики в порядке.")
        else:
            _fail("покрытие")
            failed = True

    _banner("Итог")
    if failed:
        print("  В параметре «общий прогон» — есть замечания; поправь и повтори.")
        return 1
    print("  В параметре «общий прогон» — всё ок; проект выглядит на все 100%.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
