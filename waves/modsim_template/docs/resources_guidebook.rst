##################
External Resources
##################

********************
Sphinx Documentation
********************

*

The modsim template uses Sphinx documentation. For more details on using Sphinx, see the main `Sphinx`_ documentation.

This template uses `Sphinx automodule`_ capability. This automatically reads the Sphinx-formatted docstrings
within Python files and adds it to the Sphinx pages where requested.

***
Git
***

* ``./.gitignore``
* ``./pyproject.toml``

The modsim template is intended to use `Git`_ for version control: a ``.gitignore`` file is included in the main
template directory. By default, it includes file paths and extensions that are not expected to be tracked,
such as the ``build/`` directory, Abaqus and `Cubit`_ journal files, and others.

This template uses `setuptools_scm`_ to assist with version numbering using Git metadata. A WIP tutorial on its usage
can be found as part of the `setuptools_scm WAVES Tutorial`_.

******
PyTest
******

For unit testing, `pytest`_ is implemented for the rectangle compression simulation. These tests can be found in
``modsim_package/tests/``. The prepackaged tests currently include testing on inputs passed to argparse, mesh
convergence, and helper functions used for the rectangle compression. There are 13 tests in total. Tests can be run
using ``scons unit_testing``.

