.PHONY: install run build clean test lint format

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt -r requirements-dev.txt

run:
	python src/main.py

build:
	pyinstaller build.spec --clean

build-dev:
	pyinstaller build.spec --clean --debug

clean:
	rmdir /s /q build 2>nul
	rmdir /s /q dist 2>nul
	rmdir /s /q __pycache__ 2>nul

test:
	python -m pytest tests/ -v

lint:
	ruff check src/

format:
	ruff format src/

env:
	copy .env.example .env
