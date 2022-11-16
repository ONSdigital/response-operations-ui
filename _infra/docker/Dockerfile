FROM python:3.11-slim

WORKDIR /app
RUN rm -rf node_modules
COPY . /app

RUN apt-get update -y && apt-get install -y python3-pip unzip curl gunicorn
RUN pip3 install pipenv && pipenv install --deploy --system

CMD ["gunicorn", "-b", "0.0.0.0:8080", "--workers", "4", "--timeout", "300", "response_operations_ui:create_app()"]
