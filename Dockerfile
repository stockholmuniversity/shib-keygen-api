# Don't name this PYTHON_VERSION since the python image already uses that for the full version
ARG PY_VER=3.11
FROM python:${PY_VER}-slim-bookworm AS deps
ARG PROJECT PY_VER
WORKDIR /usr/src
RUN \
  mkdir -p .venv \
  && \
  chmod -R a+rw .

# pip doesn't know about the index configured in pyproject.toml
ENV \
  HOME=/usr/src \
  PIP_INDEX_URL=https://pypi.it.su.se/repository/su-pypi-group/simple

FROM deps AS build
ARG PROJECT PY_VER

USER 1000

COPY poetry.lock pyproject.toml ./
RUN mkdir -p $PROJECT && touch $PROJECT/__init__.py
RUN pip install --prefix .venv gunicorn==23.0.0
RUN pip install --prefix .venv .[vault]
COPY poetry.lock pyproject.toml ./
COPY $PROJECT/ ./$PROJECT/
RUN pip install --prefix .venv --upgrade .
# Fix shebang...
RUN sed -i -e '1 s@#!/usr/local/bin/python@#!/usr/bin/python@' .venv/bin/*

FROM deps AS install
ARG PROJECT TAG
WORKDIR /usr/src
RUN \
  mkdir -p .venv \
  && \
  chmod -R a+rw .

# pip doesn't know about the index configured in pyproject.toml
ENV \
  HOME=/usr/src \
  PIP_INDEX_URL=https://pypi.it.su.se/repository/su-pypi-group/simple

USER 1000

RUN pip install --prefix .venv $PROJECT==$TAG
# Fix shebang...
RUN sed -i -e '1 s@#!/usr/local/bin/python@#!/usr/bin/python@' .venv/bin/*

FROM gcr.io/distroless/python3-debian12:debug-nonroot@sha256:2ddeffa65fe354c46ec2fd3fc775d9b6e0cff8ba31e21498948393af1a9a3001 AS prod
ARG PY_VER
SHELL ["/busybox/sh", "-c"]
ENV HOME=/home/nonroot
COPY --chown=65532:65532 --from=install /usr/src/.venv $HOME
ENV PATH=$HOME/bin:$PATH PYTHONPATH=$HOME/lib/python${PY_VER}/site-packages/
ENTRYPOINT ["gunicorn", "shib_keygen_api:app"]
CMD ["--bind", "0.0.0.0:8443", "--access-logfile", "-", "--keyfile", "/mnt/secret/key.pem", "--certfile", "/mnt/secret/cert.pem"]

FROM gcr.io/distroless/python3-debian12:debug-nonroot@sha256:2ddeffa65fe354c46ec2fd3fc775d9b6e0cff8ba31e21498948393af1a9a3001 AS dev
ARG PY_VER
SHELL ["/busybox/sh", "-c"]
ENV HOME=/home/nonroot
COPY --chown=65532:65532 --from=build /usr/src/.venv $HOME
ENV PATH=$HOME/bin:$PATH PYTHONPATH=$HOME/lib/python${PY_VER}/site-packages/
ENTRYPOINT ["gunicorn", "shib_keygen_api:app"]
CMD ["--bind", "0.0.0.0:8443", "--access-logfile", "-", "--keyfile", "/mnt/secret/key.pem", "--certfile", "/mnt/secret/cert.pem"]
