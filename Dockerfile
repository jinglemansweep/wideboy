ARG base_image="python"
ARG base_tag="3.10"
ARG uid="1000"

FROM ${base_image}:${base_tag} AS build
ARG uid

COPY ./pyproject.toml ./poetry.lock /app/
WORKDIR /app

RUN python -m venv /venv && \
    /venv/bin/python -m pip install --upgrade pip poetry
RUN . /venv/bin/activate && poetry install

COPY . /app
RUN . /venv/bin/activate && ls /app && cd /app/lib/rpi-rgb-led-matrix && make build-python

RUN chown -R ${uid} /app

FROM ${base_image}:${base_tag} AS runtime
ARG uid

COPY --from=build /venv /venv
COPY --from=build /app /app

WORKDIR /app
USER ${uid}

CMD ["/venv/bin/python", "-m", "wideboy"]