import os
import sys

from setuptools import setup
from setuptools import find_packages

# setup logic from github.com/jupyterhub/jupyterhub
# TODO: consolidate release mechanism with the root package.json
v = sys.version_info
if v[:2] < (3, 6):
    error = 'ERROR: IllumiDesk requires Python version 3.6 or above.'
    print(error, file=sys.stderr)
    sys.exit(1)

shell = False
if os.name in ('nt', 'dos'):
    shell = True
    warning = 'WARNING: Windows is not officially supported'
    print(warning, file=sys.stderr)

# Get the current package version.
here = os.path.abspath(os.path.dirname(__file__))
version_ns = {}
with open(os.path.join('_version.py')) as f:
    exec(f.read(), {}, version_ns)

setup(
    name='illumidesk',
    version=version_ns['__version__'],
    description='IllumiDesk core package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/illumidesk/illumidesk',
    author='The IllumiDesk Team',
    author_email='hello@illumidesk.com',
    license='MIT',
    packages=find_packages(exclude='./tests'),
    install_requires=[
        'dockerspawner==0.11.1',
        'filelock==3.0.12',
        'josepy==1.3.0',
        'jupyterhub>=1.1.0',
        'jupyterhub-ltiauthenticator>=0.4.0',
        'jwcrypto',
        'nbgrader>=0.6.1',
        'oauthenticator==0.11.0',
        'pem==20.1.0',
        'PyJWT==1.7.1',
        'pyjwkest==1.4.2',
        'pycryptodome==3.9.7',
        'pylti==0.7.0',
        'filelock==3.0.12',
        'lti==0.9.5',
    ],  # noqa: E231
    package_data={'': ['*.html'],},  # noqa: E231
)
