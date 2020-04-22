FROM python:3-alpine

WORKDIR /usr/src/app

RUN apk update \
 && apk upgrade \
 && apk add --no-cache \
    curl

RUN apk update \
 && apk add --no-cache \
 gcc \
 libc-dev \
 libffi-dev \
 libressl-dev \
 linux-headers \
 make \
 musl-dev \
 openssl-dev \
 python3-dev \
 zeromq-dev
 
RUN pip install --no-cache-dir \
    hypercorn

RUN pip3 install docker-compose

# Install illumidesk package
# there is a file dependency with illumidesk package existing in the working directory
COPY illumidesk.zip /tmp/illumidesk.zip
RUN python3 -m pip install --no-cache /tmp/illumidesk.zip

EXPOSE 8000

HEALTHCHECK CMD curl --fail http://localhost:8000/config || exit 1
