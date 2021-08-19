ARG BASE_IMAGE=python:3.8
FROM "${BASE_IMAGE}"

RUN apt-get update \
 && apt-get install unzip -y --no-install-recommends \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

# install packages with pip. makes sure pip is up to date.
COPY requirements.txt /tmp/
RUN python -m pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r /tmp/requirements.txt

# Application directory
ENV APP_DIR=/illumidesk

RUN mkdir -p "${APP_DIR}"
COPY . "${APP_DIR}"
# app folder
RUN python3 -m pip install --no-cache-dir "${APP_DIR}"/.

WORKDIR "${APP_DIR}"

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "graderservice.wsgi:app"]

HEALTHCHECK CMD curl --fail http://localhost:8000/healthcheck || exit 1
