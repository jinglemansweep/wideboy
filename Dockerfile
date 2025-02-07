ARG base_image="python"
ARG base_tag="3.11"

FROM ${base_image}:${base_tag} AS build

COPY ./pyproject.toml ./poetry.lock /app/
WORKDIR /app

RUN python -m venv /venv && \
    /venv/bin/python -m pip install --upgrade pip poetry
RUN . /venv/bin/activate && poetry install

COPY . /app
RUN . /venv/bin/activate && ls /app && cd /app/lib/rpi-rgb-led-matrix && make build-python

FROM ${base_image}:${base_tag} AS runtime

COPY --from=build /venv /venv
COPY --from=build /app /app

WORKDIR /app
USER root

CMD ["/venv/bin/python", "-m", "wideboy"]
