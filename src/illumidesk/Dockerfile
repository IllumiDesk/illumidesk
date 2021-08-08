# for kubernetes, use the --build-arg when building image or uncomment
# ARG BASE_IMAGE=jupyterhub/k8s-hub:1.1.2
ARG BASE_IMAGE=jupyterhub/jupyterhub:1.4.2
FROM "${BASE_IMAGE}"

USER root
RUN apt-get update \
 && apt-get install -y \
    curl \
    git \
    unzip \
    wget \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
RUN wget https://configs.illumidesk.com/images/illumidesk-80.png \
 && cp -r /tmp/illumidesk-80.png /srv/jupyterhub/ \
 && cp -r /tmp/illumidesk-80.png /usr/local/share/jupyterhub/static/images/illumidesk-80.png \
 && chown "${NB_UID}" /srv/jupyterhub/illumidesk-80.png

USER "${NB_UID}"

ENV PATH="/home/${NB_USER}/.local/bin:${PATH}"

# ensure pip is up to date
RUN python3 -m pip install --upgrade pip

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

WORKDIR /tmp
COPY . /tmp
RUN python3 -m pip install /tmp/.

WORKDIR /srv/jupyterhub/

# This config is overwitten with k8s setup
COPY jupyterhub_config.py /srv/jupyterhub/

CMD ["jupyterhub", "--config", "/srv/jupyterhub/jupyterhub_config.py"]
