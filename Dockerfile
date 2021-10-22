FROM python:3.6

RUN pip install poetry==1.1.9

WORKDIR /app

COPY pyproject.toml /app
COPY poetry.lock /app

RUN poetry install

ADD gradient_utils /app/gradient_utils
ADD tests /app/tests