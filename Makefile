build:
	pipenv install --dev

lint:
	pipenv run flake8 ./response_operations_ui ./tests
	pipenv check ./response_operations_ui ./tests

test: lint
	pipenv run python run_tests.py

start:
	pipenv run python run.py
