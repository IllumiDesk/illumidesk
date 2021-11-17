import contextlib
import os
import sys

import formgradernext


@contextlib.contextmanager
def mock_platform(platform):
    old_platform = sys.platform
    sys.platform = platform
    yield
    sys.platform = old_platform


def test_nbextension_linux():
    from formgradernext import _jupyter_nbextension_paths

    with mock_platform("linux"):
        nbexts = _jupyter_nbextension_paths()
        assert len(nbexts) == 1
        assert nbexts[0]["section"] == "common"
        paths = [ext["src"] for ext in nbexts]
        for path in paths:
            assert os.path.isdir(
                os.path.join(os.path.dirname(formgradernext.__file__), path)
            )
