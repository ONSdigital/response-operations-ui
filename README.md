# response-operations-ui
[![Build Status](https://travis-ci.org/ONSdigital/response-operations-ui.svg?branch=master)](https://travis-ci.org/ONSdigital/response-operations-ui)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5c72e3cdb35b487ea0f462f8b3ee4606)](https://www.codacy.com/app/andrewmil/response-operations-ui?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ONSdigital/response-operations-ui&amp;utm_campaign=Badge_Grade)
[![codecov](https://codecov.io/gh/ONSdigital/response-operations-ui/branch/master/graph/badge.svg)](https://codecov.io/gh/ONSdigital/response-operations-ui)

Run the application
-------------------
Install pipenv
```
pip install pipenv
```

Use pipenv to create a virtualenv and install dependencies
```
pipenv install
```

Once these have been installed the app can be run from the root directory using the following
```
pipenv run python run.py
```

Alternatively run with gunicorn
```
$ pipenv run gunicorn -b 0.0.0.0:8085 response_operations_ui:app -w=4
```

Alternatively run with Make

This command will build all the requirements
```
make build
```
This command will run the application
```
make start
```

When the application is running and you are required to sign-in, you will need an authenticated account,
but for now the username and password are 'user' and 'pass'

Frontend development
-------------------
Styling is implemented using scss and javascript. You can find the styling files in [the static folder](response_operations_ui/static)

When the application is run the scss files are converted into css and they are minimised into one file, `all.css.min`

Similarly the js files are minimised into one file, `all.js.min`

Test the application
--------------------
Ensure dev dependencies have been installed
```bash
pipenv install --dev
```
Run tests with coverage
```
$ pipenv run python run_tests.py
```

Run linting (the travis build sets a custom max line length)
```
$ pipenv check --style . --max-line-length 120
```

Run tests with Make
```
make test
```
