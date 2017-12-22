FROM python:3.6

WORKDIR /response_operations_ui
COPY . /response_operations_ui
EXPOSE 8085
RUN pip3 install pipenv==8.3.1 && pipenv install --deploy --system

ENTRYPOINT ["python3"]
CMD ["run.py"]