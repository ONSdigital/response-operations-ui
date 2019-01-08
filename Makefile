build:
	pipenv install --dev
	rm -rf node_modules
	npm install
	node_modules/gulp/bin/gulp.js build

lint:
	pipenv run flake8 --exclude ./response_operations_ui/logger_config.py ./response_operations_ui ./tests
	pipenv check ./response_operations_ui ./tests

test: lint
	pipenv run python run_tests.py
	node_modules/gulp/bin/gulp.js lint

start:
	node_modules/gulp/bin/gulp.js build
	pipenv run python run.py

docker: test
	docker build -t sdcplatform/response-operations-ui:latest .
