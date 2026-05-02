# GhostPrint Makefile

.PHONY: help install install-dev test lint clean build publish

help:
	@echo "GhostPrint Makefile commands:"
	@echo "  install      - Install GhostPrint"
	@echo "  install-dev  - Install in development mode"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting (flake8, black)"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build distribution packages"
	@echo "  publish      - Publish to PyPI"

install:
	pip install -e .

install-dev:
	pip install -e .
	pip install -r requirements.txt

test:
	pytest -v

lint:
	flake8 ghostprint/
	black --check ghostprint/
	mypy ghostprint/

format:
	black ghostprint/
	isort ghostprint/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python setup.py sdist bdist_wheel

publish: build
	twine upload dist/*

docker-build:
	docker build -t ghostprint:latest .

docker-run:
	docker run -it ghostprint:latest

run-tests:
	pytest tests/ -v --cov=ghostprint --cov-report=html