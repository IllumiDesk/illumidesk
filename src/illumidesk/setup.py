import os
import sys

from setuptools import find_packages
from setuptools import setup

# setup logic from github.com/jupyterhub/jupyterhub
# TODO: consolidate release mechanism with the root package.json
v = sys.version_info
if v[:2] < (3, 6):
    error = "ERROR: IllumiDesk requires Python version 3.6 or above."
    print(error, file=sys.stderr)
    sys.exit(1)

shell = False
if os.name in ("nt", "dos"):
    shell = True
    warning = "WARNING: Windows is not officially supported"
    print(warning, file=sys.stderr)

# Get the current package version.
here = os.path.abspath(os.path.dirname(__file__))
version_ns = {}
with open(os.path.join("_version.py")) as f:
    exec(f.read(), {}, version_ns)

setup(
    name="illumidesk",
    version=version_ns["__version__"],
    description="IllumiDesk core package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/illumidesk/illumidesk",
    author="The IllumiDesk Team",
    author_email="hello@illumidesk.com",
    license="Apache 2.0",
    packages=find_packages(),
    install_requires=[
        "josepy==1.4.0",
        "jupyterhub-kubespawner==0.14.1",
        "jupyterhub-ltiauthenticator==1.3.0",
        "jwcrypto==0.8",
        "nbgrader==0.6.2",
        "oauthlib==3.1",
        "oauthenticator>=0.13.0",
        "pem==20.1.0",
        "psycopg2-binary==2.8.6",
        "PyJWT>=1.7.1,<2",
        "pyjwkest>=1.4.2",
        "pycryptodome==3.9.8",
        "SQLAlchemy-Utils==0.36.8",
    ],  # noqa: E231
    package_data={
        "": ["*.html"],
    },  # noqa: E231
)
