import os

from setuptools import find_packages
from setuptools import setup

name = "async_nbgrader"
here = os.path.abspath(os.path.dirname(__file__))
version_ns = {}
with open(os.path.join(here, name, "_version.py")) as f:
    exec(f.read(), {}, version_ns)

setup_args = dict(
    name=name,
    version=version_ns["__version__"],
    packages=find_packages(),
    package_data={
        'async_nbgrader.tests': [
            'apps/files/*',
        ]
    },
    entry_points={
        "console_scripts": ["ild=async_nbgrader.apps.async_nbgraderapp:main"]
    },
    install_requires=[
        "jupyter_core>=4.7.1",
        "notebook>=6.4.2",
        "nbgrader>=0.6.2",
        "pika>=1.2.0",
    ],
    tests_require=[
        "pytest-rabbitmq>=2.2.0",
        "pytest-env>=0.6.2",
    ],
    include_package_data=True,
)

if __name__ == "__main__":
    setup(**setup_args)
