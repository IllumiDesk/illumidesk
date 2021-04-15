ARG BASE_IMAGE=jupyterhub/k8s-hub:0.11.1
FROM "${BASE_IMAGE}"

USER root
RUN apt-get update \
 && apt-get install -y \
    unzip \
    wget \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
RUN wget https://configs.illumidesk.com/images/illumidesk-80.png \
 && cp -r /tmp/illumidesk-80.png /srv/jupyterhub/ \
 && chown "${NB_UID}" /srv/jupyterhub/illumidesk-80.png

USER "${NB_UID}"

ENV PATH="/home/${NB_USER}/.local/bin:${PATH}"

# illumidesk package release
ARG ILLUMIDESK_VERSION=2.0.0

# ensure pip is up to date
RUN python3 -m pip install --upgrade pip

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

WORKDIR /tmp
#RUN wget "https://github.com/IllumiDesk/illumidesk/archive/v${ILLUMIDESK_VERSION}.zip" \
# && unzip "/tmp/v${ILLUMIDESK_VERSION}.zip"
#WORKDIR "/tmp/illumidesk-${ILLUMIDESK_VERSION}/src/illumidesk/"
COPY . /tmp
RUN python3 -m pip install /tmp/.

WORKDIR /srv/jupyterhub/

# This config is overwitten with k8s setup
COPY jupyterhub_config.py /srv/jupyterhub/
COPY wait-for-postgres.sh /srv/jupyterhub/
RUN chmod +rx wait-for-postgres.sh

CMD ["./wait-for-postgres.sh", "jupyterhub", "--config", "/srv/jupyterhub/jupyterhub_config.py"]
