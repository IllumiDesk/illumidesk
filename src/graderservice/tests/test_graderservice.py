from graderservice.graderservice import GraderServiceLauncher


def test_initializer_sets_api_token_from_env_var(monkeypatch, grader_setup_environ):
    """
    Does initializer set the api token correctly?
    """
    local_org = "acme"
    local_course = "intro101"
    local_is_debug = True
    launcher = GraderServiceLauncher(org_name=local_org, course_id=local_course)
    assert launcher.grader_is_debug is False

    launcher = GraderServiceLauncher(
        org_name=local_org, course_id=local_course, is_debug=local_is_debug
    )
    assert launcher.grader_is_debug is True
