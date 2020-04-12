import json
import pytest
from unittest.mock import patch
from illumidesk.setup_course.course import Course

@pytest.fixture(scope="function")
def setup_course_environ(monkeypatch, tmp_path):
    monkeypatch.setenv('NFS_ROOT', str(tmp_path))
    monkeypatch.setenv('NB_UID', '10001')
    monkeypatch.setenv('NB_GID', '100')

@pytest.fixture(scope='function')
def test_client(monkeypatch, tmp_path):
    monkeypatch.setenv('JUPYTERHUB_CONFIG_PATH', str(tmp_path))
    # important than environ reads JUPYTERHUB_CONFIG_PATH variable before 
    # app initialization 
    from illumidesk.setup_course.app import app
    return app.test_client()

@pytest.mark.asyncio
async def test_config_path_returns_empty_dict(test_client):
    response = await test_client.get('/config')
    assert response.status_code == 200
    data = await response.get_data(raw=False)
    data_as_json = json.loads(data)
    assert data_as_json['services'] is not None
    assert data_as_json['load_groups'] is not None

@pytest.mark.asyncio
async def test_post_method_returns_BadRequest_without_data(test_client):    
    response = await test_client.post('/')
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_post_method_result_indicates_when_a_new_setup_was_created(setup_course_environ, test_client):
    async def return_async_value():
        return True
    
    with patch.object(
        Course, 'setup', side_effect=return_async_value):

        data = {
            'org': 'my_company',
            'course_id': 'course01',
            'domain': 'example.com',
        }

        response = await test_client.post('/', json=data)
        resp_data = await response.get_data(raw=False)
        print('response.status_code', response.status_code)
        assert 'is_new_setup' in resp_data

@pytest.mark.asyncio
async def test_post_method_creates_new_service_definition_in_config(setup_course_environ, test_client):
    async def return_async_value():
        return True
    
    with patch.object(
        Course, 'setup', side_effect=return_async_value):

        data = {
            'org': 'my_company',
            'course_id': 'course01',
            'domain': 'example.com',
        }
        # create the course
        _ = await test_client.post('/', json=data)
        # check the jupyterhub config file 
        config_response = await test_client.get('/config')
        response_data = await config_response.get_data(raw=False)
        data_as_json = json.loads(response_data)

        exists = True
        for service in data_as_json['services']:
            if data['course_id'] in service:
                exists = True
        
        assert exists == True
