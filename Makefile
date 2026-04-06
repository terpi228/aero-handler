# Удобные цели для разработки (на Windows без make — см. README: python scripts/dev_check.py)

.PHONY: check check-ci check-cov format lint test

check:
	python scripts/dev_check.py

check-ci:
	python scripts/dev_check.py --ci

check-cov:
	python scripts/dev_check.py --cov

format:
	python -m isort .
	python -m black .

lint:
	python -m flake8 .

test:
	python -m pytest -q
