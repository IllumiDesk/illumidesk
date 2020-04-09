import json
import logging
import os
import pprint
import re
import requests
import shutil
import sys
import time

from filelock import FileLock
from io import StringIO
from pathlib import Path
from secrets import token_hex

import docker
from docker.errors import APIError
from flask import Flask
from flask import request
from .course import Course


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask("setup-course-app")


JSON_FILE_PATH = os.environ.get('JUPYTERHUB_CONFIG_PATH') + '/jupyterhub_config.json'

cache = {'services': [], 'load_groups': {}}

with Path(JSON_FILE_PATH).open('w+') as config:
    try:
        cache = json.load(config)
    except json.JSONDecodeError:
        if Path(JSON_FILE_PATH).stat().st_size != 0:
            raise
        else:
            json.dump(cache, config)


@app.route("/", methods=['POST'])
def main():
    data = request.get_json()
    logger.debug('Received data payload %s' % data)
    try:
        is_new_setup = Course(**data).setup()
        logger.debug('Is this a new setup? %s' % is_new_setup)
    except Exception as e:
        logger.error("Unable to complete course setup", exc_info=True)
        return {'error': 500}
    return {
        'message': 'OK',
        'is_new_setup': f'{is_new_setup}'
    }

@app.route("/config", methods=['GET'])
def config():
    return json.dumps(cache)

@app.route("/restart", methods=['POST'])
def restart():
    logger.debug('Received request to restart jupyterhub')
    utils = SetupUtils()
    try:
        utils.restart_jupyterhub()
        logger.debug('Restarting jupyterhub')
    except Exception as e:
        logger.error("Unable to restart the container", exc_info=True)
        return {'error': 500}
    return {'message': 'OK'}


class SetupUtils:
    """
    Utils class used to manage course setup configurations and updates.
    """
    def restart_jupyterhub(self):
        """
        Restart jupyterhub using the docker client after updating configs.

        Raises:
          ContainerException if the container could not be restarted.
        """
        logger.debug('Received request to restart JupyterHub')
        jupyterhub_container_name = os.environ.get('JUPYTERHUB_SERVICE_NAME')
        containers = self.client.containers.list(filters={'name': f'{jupyterhub_container_name}'})
        for container in containers:
            logger.debug('Found container %s, restarting ...' % jupyterhub_container_name)
            try:
                container.restart()
            except docker.errors.NotFound:
                logger.error('Grader container not found')

