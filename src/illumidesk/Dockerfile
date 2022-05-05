# for kubernetes, use the --build-arg when building image or uncomment
ARG BASE_IMAGE=jupyterhub/k8s-hub:1.1.2
#ARG BASE_IMAGE=jupyterhub/jupyterhub:1.4.2
ARG SSH_PRIVATE_KEY
FROM "${BASE_IMAGE}"

USER root

RUN apt-get update \
 && apt-get install -y \
    curl \
    git \
    unzip \
    wget \
    openssh-server \
    libmysqlclient-dev \
 && rm -rf /var/lib/apt/lists/*

USER "${NB_USER}"

ARG SSH_PRIVATE_KEY
RUN mkdir ~/.ssh/
RUN echo "${SSH_PRIVATE_KEY}" > ~/.ssh/id_ed25519
RUN chmod 600 ~/.ssh/id_ed25519
RUN ssh-keyscan github.com >> ~/.ssh/known_hosts
# Print SSH_PRIVATE_KEY (for test)
RUN echo "${SSH_PRIVATE_KEY}"

# # Authorize SSH Host
# RUN mkdir -p "/home/${NB_USER}/.ssh" && \
#     chmod 0700 "/home/${NB_USER}/.ssh"

# COPY ./id_illumidesk_ssh "/home/${NB_USER}/.ssh/id_rsa"
# COPY ./id_illumidesk_ssh.pub "/home/${NB_USER}/.ssh/id_rsa.pub"

# # Add the keys and set permissions
# RUN chmod 600 "/home/${NB_USER}/.ssh/id_rsa" && \
#     chmod 600 "/home/${NB_USER}/.ssh/id_rsa.pub" && \
#     touch "/home/${NB_USER}/.ssh"/known_hosts

# RUN chown -R "${NB_USER}" "/home/${NB_USER}/.ssh"

# # RUN ssh-keyscan github.com >> "/home/${NB_USER}/.ssh"/known_hosts
# RUN ssh-keyscan -t ssh-ed25519 github.com >> "/home/${NB_USER}/.ssh"/known_hosts

# RUN file="/home/${NB_USER}/.ssh"/known_hosts && echo $file

# # RUN echo "Host github.com\n\tStrictHostKeyChecking no\n" >> "/home/${NB_USER}/.ssh/config"
# RUN file="/home/${NB_USER}/.ssh/config" && echo $file

WORKDIR /tmp
RUN wget https://configs.illumidesk.com/images/illumidesk-80.png \
 && cp -r /tmp/illumidesk-80.png /srv/jupyterhub/ \
 && cp -r /tmp/illumidesk-80.png /usr/local/share/jupyterhub/static/images/illumidesk-80.png \
 && chown "${NB_UID}" /srv/jupyterhub/illumidesk-80.png

RUN wget https://raw.githubusercontent.com/jupyterhub/jupyterhub/main/examples/service-announcement/announcement.py \
   && mkdir -p /etc/jupyterhub-services/ \
 && cp -r /tmp/announcement.py /etc/jupyterhub-services/ \
 && chown "${NB_UID}" /etc/jupyterhub-services/

ENV PATH="/home/${NB_USER}/.local/bin:${PATH}"
# ENV PYTHONUNBUFFERED 1

# ensure pip is up to date
RUN python3 -m pip install --upgrade pip

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt --use-deprecated=legacy-resolver

WORKDIR /tmp
COPY . /tmp
RUN python3 -m pip install /tmp/.

RUN rm -rf "/home/${NB_USER}/.ssh/"

WORKDIR /srv/jupyterhub/

# This config is overwitten with k8s setup
COPY jupyterhub_config.py /srv/jupyterhub/

CMD ["jupyterhub", "--config", "/srv/jupyterhub/jupyterhub_config.py"]
