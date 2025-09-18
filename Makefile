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
	pipenv run isort .
	pipenv run black --line-length 120 .
	pipenv run djlint response_operations_ui/
	pipenv run flake8 --exclude ./node_modules

lint-check: load-design-system-templates
	pipenv run isort . --check-only
	pipenv run black --line-length 120 --check .
	pipenv run djlint response_operations_ui/
	pipenv run flake8 --exclude ./node_modules

test: lint-check
	pipenv run python run_tests.py
	rm -rf ./flask_session

test-html: lint-check
	pipenv run python run_tests.py html
	rm -rf ./flask_session

start: load-design-system-templates
	pipenv run python run.py

watch_and_start:
	pipenv run python run.py

docker: test
	docker build -t sdcplatform/response-operations-ui:latest .
