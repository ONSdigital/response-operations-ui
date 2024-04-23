DESIGN_SYSTEM_VERSION=`cat .design-system-version`

build:
	pipenv install --dev

build-docker:
	docker build .

build-kubernetes:
	docker build -f _infra/docker/Dockerfile .

load-design-system-templates:
	pipenv run ./scripts/load_templates.sh $(DESIGN_SYSTEM_VERSION)

lint:
	pipenv check ./response_operations_ui ./tests
	pipenv run isort .
	pipenv run black --line-length 120 .
	pipenv run djlint .
	pipenv run flake8 --exclude ./node_modules

lint-check: load-design-system-templates
	pipenv check ./response_operations_ui ./tests

	pipenv run isort . --check-only
	pipenv run black --line-length 120 --check .
	pipenv run djlint . 
	pipenv run flake8 --exclude ./node_modules

test: lint-check
	pipenv run python run_tests.py
	rm -rf ./flask_session

start: load-design-system-templates
	pipenv run python run.py

watch_and_start:
	pipenv run python run.py

docker: test
	docker build -t sdcplatform/response-operations-ui:latest .

minify-install:
	npm init -y
	npm install webpack@5.76.0  @ampproject/remapping@2.2.1 --save-dev
	#npm install node-sass sass-loader file-loader resolve-url-loader --save-dev
	#npm install -D babel-loader @babel/core@22.10 --save-dev

minify:
	npx webpack --mode=production
