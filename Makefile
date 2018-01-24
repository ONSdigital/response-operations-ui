build:
	pipenv install
	pipenv install --dev

test:
	pipenv check --style ./response_operations_ui ./tests
	pipenv run python run_tests.py
