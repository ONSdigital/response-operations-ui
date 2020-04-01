# response-operations-ui

[![Build Status](https://travis-ci.org/ONSdigital/response-operations-ui.svg?branch=master)](https://travis-ci.org/ONSdigital/response-operations-ui)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5c72e3cdb35b487ea0f462f8b3ee4606)](https://www.codacy.com/app/andrewmil/response-operations-ui?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ONSdigital/response-operations-ui&amp;utm_campaign=Badge_Grade)
[![codecov](https://codecov.io/gh/ONSdigital/response-operations-ui/branch/master/graph/badge.svg)](https://codecov.io/gh/ONSdigital/response-operations-ui)

## Run the application

Install pipenv

```bash
pip install pipenv
```

Use pipenv to create a virtualenv and install dependencies

```bash
pipenv install
```

Ensure you have Node.js version >=10 installed.  The recommended way to do this is to use Creationix Node Version Manager, which works on Linux and MacOSX systems:

```bash
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash
```

After this, run

```bash
nvm use
```

...and the node version specified in `.nvmrc` will be selected.

Then, you only need run

```bash
npm install
```

...and the task runner will be installed

You can run gulp tasks using `npm run gulp <taskname>`, or just `gulp` if you have `gulp` globally installed (`npm i -g gulpjs`)

For a basic build, you can just have node >=10 installed, and run `make build` to run any build tasks, which includes the installation of node packages, and running compilation/transpilation tasks.

Once these have been installed the app can be run from the root directory using the following

```bash
pipenv run python run.py
```

Alternatively run with gunicorn

```bash
pipenv run gunicorn -b 0.0.0.0:8085 response_operations_ui:app -w=4
```

Alternatively run with Make

This command will build all the requirements

```bash
make build
```

This command will run the application

```bash
make start
```

When the application is running and you are required to sign-in, you will need an authenticated account,
but for now the username and password are 'user' and 'pass'

## Frontend development

Styling is implemented using scss and javascript. You can find the styling files in [the static folder](response_operations_ui/static)

When the application is run the scss files are converted into css and they are minimised into one file, `all.css.min`

Similarly the js files are minimised into one file, `all.js.min`

## Test the application

Ensure dev dependencies have been installed

```bash
pipenv install --dev
```

Run tests with coverage

```bash
pipenv run python run_tests.py
```

Run linting (the travis build sets a custom max line length)

```bash
pipenv check --style . --max-line-length 120
```

Run tests with Make

```bash
make test
```

If you get a `Too many open files` error, then run the following to fix it

```bash
ulimit -Sn 10000
```
