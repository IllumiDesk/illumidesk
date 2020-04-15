import json
import logging
import os
import pprint
import re
import shutil
import sys
import time

from filelock import FileLock
from io import StringIO
from pathlib import Path
from secrets import token_hex

from quart import Quart
from quart import request
from quart.exceptions import BadRequest
from .course import Course
from .utils import SetupUtils


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Quart("setup-course-app")

configs_path = os.environ.get('JUPYTERHUB_CONFIG_PATH', '/srv/jupyterhub')

Path(configs_path).mkdir(exist_ok=True, parents=True)


JSON_FILE_PATH =  configs_path + '/jupyterhub_config.json'

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
async def main():
    data = await request.get_json()
    if data is None:
        raise BadRequest()
    logger.debug('Received data payload %s' % data)
    try:
        new_course = Course(**data)
        is_new = await new_course.setup()
        logger.debug('Is this a new setup? %s' % is_new)
        # update the jupyterhub config to include new service info
        update_jupyterhub_config(new_course)
    except Exception as e:
        logger.error("Unable to complete course setup", exc_info=True)
        return {'error': 500, 'detail': str(e)}
    return {
        'message': 'OK',
        'is_new_setup': f'{is_new}'
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

def update_jupyterhub_config(course: Course):
    """
    We can add groups and users with the REST API, but not services. Therefore
    add new services to the JupyterHub.services section within the jupyterhub 
    configuration file (jupyterhub_config.py).
    
    """
    jupyterhub_config_json = Path(JSON_FILE_PATH)
    # Lock file to manage jupyterhub_config.py
    jupyterhub_lock = os.environ.get('JUPYTERHUB_CONFIG_PATH') + '/jhub.lock'
    service_config = course.get_service_config()

    load_group = {f'formgrade-{course.course_id}': [course.grader_name]}
    if not any(s for s in cache['services'] if s['url'] == service_config['url']):
        cache['services'].append(service_config)
    cache['load_groups'].update(load_group)
    lock = FileLock(str(jupyterhub_lock))
    with lock:
        with jupyterhub_config_json.open('r+') as config:
            json.dump(cache, config)