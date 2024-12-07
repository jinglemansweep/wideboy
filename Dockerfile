FROM python:3.10

COPY . /app
WORKDIR /app

RUN python -m venv /venv && \
    python -m pip install --upgrade pip poetry && \
    poetry install

