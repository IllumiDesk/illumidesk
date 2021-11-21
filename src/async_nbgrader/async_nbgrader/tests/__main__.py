import os
import sys

import pytest

testdir = os.path.dirname(__file__)
pytest.main(sys.argv[1:] + [testdir])
