.PHONY: install test test-cov clean lint format

install:
	pip install -e ".[dev]"

test:
	pytest

test-cov:
	pytest --cov-report=html --cov-report=term

lint:
	black --check aion_engine tests
	isort --check-only aion_engine tests

format:
	black aion_engine tests
	isort aion_engine tests

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/
