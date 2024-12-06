# response-operations-ui
bump
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

### Load the ONS Design System Templates
```
make load-design-system-templates
```

This command will take the version number defined in the `.design-system-version` file and download the templates for that version of the Design System. It will also be automatically run when running `make start`.

To update to a different version of the Design System:
- update the version number in the `.design-system-version` file
- run `make load-design-system-templates` script

### Specific response-operations-ui styling and js
Styling is implemented using scss and javascript. You can find the styling files in [the static folder](response_operations_ui/static)

When the application is run the scss files are converted into css and they are minimised into one file, `all.css.min`

Similarly the js files are minimised into one file, `all.js.min`

It is a manual step to minimise the JavaScript

```bash
make minify-install
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
