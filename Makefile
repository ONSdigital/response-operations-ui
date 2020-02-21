build:
	pipenv install --dev
	rm -rf node_modules
	npm install
	npx gulp build

build-docker:
	docker build .

build-kubernetes:
	docker build -f _infra/docker/Dockerfile .

lint:
	pipenv run flake8 --exclude=./node_modules,./response_operations_ui/logger_config.py ./response_operations_ui ./tests
	pipenv check ./response_operations_ui ./tests
	npx gulp lint

test: lint
	npm test
	pipenv run python run_tests.py

start:
	npx gulp build
	pipenv run python run.py

watch:
	npx gulp watch

watch_and_start:
	npx gulp build
	npx gulp watch
	pipenv run python run.py

docker: test
	docker build -t sdcplatform/response-operations-ui:latest .

load-templates:
	pipenv run ./scripts/load_templates.sh
