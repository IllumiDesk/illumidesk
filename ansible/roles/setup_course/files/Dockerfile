ARG BASE_IMAGE={{docker_jhub_base_image}}
FROM ${BASE_IMAGE}

WORKDIR /usr/src/app
 
RUN python3 -m pip install --no-cache-dir \
    docker-compose \
    hypercorn

# Install illumidesk package from copied files, which allows us
# to test working branches.
# TODO: create new version for staging/production with specific version from
# github and/or pypi release tag
COPY illumidesk.zip /tmp/illumidesk.zip
RUN python3 -m pip install --no-cache /tmp/illumidesk.zip \
 && rm /tmp/illumidesk.zip

EXPOSE 8000

HEALTHCHECK CMD curl --fail http://localhost:8000/config || exit 1
