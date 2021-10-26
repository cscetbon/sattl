FROM python:3.8-alpine AS base

RUN pip install pip --upgrade
RUN apk add --no-cache --virtual .build-deps build-base libffi-dev
WORKDIR /app
COPY setup.py setup.cfg ./
COPY sattl sattl
RUN pip install --no-cache-dir -e .
RUN apk del --no-cache .build-deps

ENTRYPOINT ["sattl"]

FROM base AS tests

RUN pip install --no-cache-dir -e '.[testing]'
COPY tests tests
COPY .github/workflows/config.json.sample config.json

ENTRYPOINT ["pytest"]
