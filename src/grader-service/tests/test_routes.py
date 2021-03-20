def test_healthcheck(app, client):
    """Ensure the healthcheck endpoint returns a 200 (OK) status code."""
    res = client.get("/healthcheck", method="GET")
    assert res.status_code == 200
