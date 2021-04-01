build:
	pipenv install --dev

build-docker:
	docker build .

build-kubernetes:
	docker build -f _infra/docker/Dockerfile .

lint:
	pipenv run flake8 --exclude=./node_modules,./response_operations_ui/logger_config.py ./response_operations_ui ./tests
	pipenv check ./response_operations_ui ./tests

test: lint
	pipenv run python run_tests.py

start:
	pipenv run python run.py

watch_and_start:
	pipenv run python run.py

docker: test
	docker build -t sdcplatform/response-operations-ui:latest .

load-templates:
	pipenv run ./scripts/load_templates.sh

minify-install:
	npm init -y
	npm install webpack webpack-cli node-sass sass-loader file-loader resolve-url-loader --save-dev
	npm install -D babel-loader @babel/core @babel/preset-env webpack

minify:
	npx webpack
