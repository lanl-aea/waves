# Required for conda build, which doesn't use pyproject.toml yet
from setuptools import setup
setup(
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
)
