ARG BASE_IMAGE={{docker_illumidesk_jhub_image}}
FROM ${BASE_IMAGE}

WORKDIR /usr/src/app
 
RUN python3 -m pip install --no-cache-dir \
    docker-compose \
    hypercorn

EXPOSE 8000

HEALTHCHECK CMD curl --fail http://localhost:8000/config || exit 1
