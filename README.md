# response-operations-ui

The frontend for the internal ONS users to administer collection exercises, messages to and from respondents, etc

## Run the application

Install pipenv

```bash
pip install pipenv
```

Use pipenv to create a virtualenv and install dependencies

```bash
pipenv install
```
And run the application using
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

### Load the ONS Design System Templates
```
make load-design-system-templates
```

This command will take the version number defined in the `.design-system-version` file and download the templates for that version of the Design System. It will also be automatically run when running `make start`.

To update to a different version of the Design System:
- update the version number in the `.design-system-version` file
- run `make load-design-system-templates` script

### Specific response-operations-ui styling and js
Styling and frontend scripts are implemented using scss and javascript. You can find the minimised files in 
[the static folder](response_operations_ui/static) and the working files in [the assets folder](response_operations_ui/assets).

Each of these working files are minimised into respective css and js files which are loaded when the application is run.
The scss files are minimised into one file, `all.css` and the js files are minimised into two files, `main.js.min` and 
`selected_ci_functions.min.js`

It is a manual step to minimise the JavaScript and scss.

Ensure you have Node.js version >=24 installed.  The recommended way to do this is to use Creationix Node Version Manager, which works on Linux and MacOSX systems:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
```

After this, run

```bash
nvm install
```

to select the version specified in `.nvmrc`

Then to install the necessary node packages and minify files, run:

```bash
npm install
make minify
```

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

or if you wish to generate an HTML report viewable at htmlcov/index.html
```bash
make test-html
```

If you get a `Too many open files` error, then run the following to fix it

```bash
ulimit -Sn 10000
```

## Known issues
If `isort` is making GitHub Actions fail with incorrectly sorted imports, check if a folder called `flask session` was created. Delete this and run the linting process again with

```bash
make lint
```

## Acceptance tests and Incognito mode
This app seems to have a problem working locally in incognito mode and through selenium tests. The problem can be traced to Talisman, disabling talisman allows the app to run locally in incognito and also allows acceptance tests to run without strange errors.

The helm chart makes `test.enabled` available which does the following:
- disables WTF csrf
- disables Flask Talisman
- disables the restriction on not being able to create collection exercise dates in the past
By default this config is set to False giving us the full security that Talisman and CSRFProtect offers. NB. the issue with testing only appears when running on a local setup, there is no such issue in preprod. It doesn't seem to work locally even if you change your /etc/hosts to simulate a FQDN with a standard TLD.

The combination of this config change for testing allows us to run the app for local development and also allows us to run acceptance tests through selenium.
