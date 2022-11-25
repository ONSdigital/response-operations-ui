FROM python:3.11-slim

WORKDIR /app
RUN rm -rf node_modules
COPY . /app
EXPOSE 8085
RUN apt-get update -y && apt-get install -y python3-pip unzip curl
RUN pip3 install pipenv && pipenv install --deploy --system

# Run the app
ENTRYPOINT ["python3"]
CMD ["run.py"]
