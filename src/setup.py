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
    packages=find_packages(),
    install_requires=[
        'ansible>=2.9',
        'jupyterhub-ltiauthenticator>=0.4.0',
        'nbgrader>=0.6.1',
        'jupyterhub>=1.1.0',
    ],
    package_data={'': ['*.html'],},
    entry_points={
        'jupyterhub.authenticators': [
            'illumidesklti11 = illumidesk.authenticators.authenticator.LTI11Authenticator',
        ],
    },
)
