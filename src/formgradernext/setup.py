import os

from setuptools import find_packages
from setuptools import setup

name = "formgradernext"
here = os.path.abspath(os.path.dirname(__file__))
version_ns = {}
with open(os.path.join(here, name, "_version.py")) as f:
    exec(f.read(), {}, version_ns)

setup_args = dict(
    name=name,
    version=version_ns["__version__"],
    packages=find_packages(),
    install_requires=[
        "nbgrader==0.6.2",
    ],
    include_package_data=True,
)

if __name__ == "__main__":
    setup(**setup_args)
