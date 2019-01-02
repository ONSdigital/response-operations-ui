FROM python:3.6-slim

WORKDIR /app
COPY . /app
EXPOSE 8085

# Python install
RUN apt-get update -y && apt-get install -y python-pip && apt-get update -y && apt-get install -y curl
RUN pip3 install pipenv && pipenv install --deploy --system


# Node Install
# Installs cUrl, uses cUrl to grab and run install script to add deb repos, installs node from this, installs build essentials to allow node-gyp
# to compile C++ bindings, runs node -v and npm -v to ensure they actually run.
RUN apt-get install -y curl \
        && curl -sL https://deb.nodesource.com/setup_10.x | bash \
        && apt-get install -y nodejs \
        && apt-get install -y build-essential
RUN node -v && npm -v

# Run the app
ENTRYPOINT ["python3"]
CMD ["run.py"]
