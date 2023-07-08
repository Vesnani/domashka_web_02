FROM python:3.11-alpine

WORKDIR /app

RUN pip install poetry

COPY poetry.lock pyproject.toml /app/

COPY . /app/

CMD poetry run python domashka_web_2.py
