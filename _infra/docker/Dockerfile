FROM python:3.6-slim

WORKDIR /app
RUN rm -rf node_modules
COPY . /app

RUN apt-get update -y && apt-get install -y python-pip unzip curl gunicorn
RUN pip3 install pipenv && pipenv install --deploy --system

# Node Install
# Installs cUrl, uses cUrl to grab and run install script to add deb repos, installs node from this, installs build essentials to allow node-gyp
# to compile C++ bindings, runs node -v and npm -v to ensure they actually run.
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash && apt-get install -y nodejs && apt-get install -y build-essential
RUN node -v && npm -v
RUN npm install --unsafe-perms
RUN npm rebuild node-sass
RUN npm run gulp build

CMD ["gunicorn", "-b", "0.0.0.0:8080", "--workers", "4", "--timeout", "60", "response_operations_ui:create_app()"]
