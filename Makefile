build:
	pipenv install --dev

lint:
	pipenv run flake8 --exclude ./response_operations_ui/logger_config.py ./response_operations_ui ./tests ./node_modules
	pipenv check ./response_operations_ui ./tests

test: lint
	pipenv run python run_tests.py

start:
	pipenv run python run.py

docker: test
	docker build -t sdcplatform/response-operations-ui:latest .
