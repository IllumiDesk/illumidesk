def test_healthcheck(client):
    """Ensure the healthcheck endpoint returns a 200 (OK) status code."""
    with client as c:
        resp = client.get("/healthcheck")
        assert resp.status_code == 200


def test_get_services_from_services_endpoint(client):
    """Ensure the services endpoint returns the correct services items in the response."""
    with client as c:
        resp = c.get("/services")
        json_data = resp.get_json()
        assert json_data["services"][0]["name"] == "foo"
        assert json_data["services"][0]["url"] == "http://intro101:8888"
        assert json_data["services"][0]["oauth_no_confirm"]
        assert json_data["services"][0]["admin"]
        assert json_data["services"][0]["api_token"] == "abc123abc123"
        assert resp.status_code == 200


def test_get_groups_from_services_endpoint(client):
    """Ensure the services endpoint returns the correct group items in the response."""
    with client as c:
        resp = c.get("/services")
        json_data = resp.get_json()
        assert json_data["groups"]["formgrade-intro101"] == ["grader-intro101"]
        assert resp.status_code == 200
