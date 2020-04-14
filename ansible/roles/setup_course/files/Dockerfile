FROM python:3-alpine

WORKDIR /usr/src/app

RUN apk update \
 && apk upgrade \
 && apk add --no-cache \
    curl    

RUN apk update \
    && apk add --no-cache \
    gcc \
    libressl-dev \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev \
    linux-headers zeromq-dev
 
RUN pip install --no-cache-dir \
    hypercorn

# Install illumidesk package
# there is a file dependency with illumidesk package existing in the working directory
COPY illumidesk.zip /tmp/illumidesk.zip
RUN python3 -m pip install --no-cache /tmp/illumidesk.zip

EXPOSE 8000

HEALTHCHECK CMD curl --fail http://localhost:8000/config || exit 1
