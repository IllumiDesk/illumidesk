# for kubernetes, use the --build-arg when building image or uncomment
# ARG BASE_IMAGE=illumidesk/k8s-hub:1.1.2
ARG BASE_IMAGE=illumidesk/jupyterhub:1.4.2
FROM "${BASE_IMAGE}"

USER "${NB_UID}"

# ensure pip is up to date
RUN python3 -m pip install --upgrade pip

WORKDIR /tmp
COPY . /tmp
RUN python3 -m pip install -e /tmp/.

WORKDIR /srv/jupyterhub/

# This config is overwitten with k8s setup
COPY jupyterhub_config.py /srv/jupyterhub/

CMD ["jupyterhub", "--config", "/srv/jupyterhub/jupyterhub_config.py"]
