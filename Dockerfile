ARG PY_VERSION="3.8"
ARG DIST="slim-stretch"

FROM python:${PY_VERSION}-${DIST}

RUN pip install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

COPY openpandemic ./openpandemic
