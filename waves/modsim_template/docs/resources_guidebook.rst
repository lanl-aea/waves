##################
External Resources
##################

********************
Sphinx Documentation
********************

* ``docs/conf.py.in``
* ``report/conf.py.in``
* ``docs/_static/custom.css``

The modsim template makes use of Sphinx documentation, which uses complied `reStructuredText`_ :cite:`rst`. For more
details on using Sphinx, see the main `Sphinx`_ documentation :cite:`sphinx`.

This template uses `Sphinx automodule`_ capability. This automatically reads the Sphinx-formatted docstrings
within Python files and adds it to the Sphinx pages where requested.

The Sphinx configuration file ``conf.py.in`` is set up with the modsim template metadata, variables, extensions, and
settings required to build the documentation. Note the added ``.in`` extension for parameter substitution compatibility.
It also includes definition of mock modules required to run the `Sphinx automodule`_ on functions expecting specific
environment configurations. For the rectangle simulation, mock modules for Abaqus and `Cubit`_ :cite:`cubit` are
required to parse all dosctrings. A custom theme is defined in the configuration file: ``_static/custom.css``. The
theme is defined in HTML format and, for the template, simply defines the max width of the generated pages.

The modsim template sets up separate building of the documentation and the report. The report uses its own shorter
``conf.py.in``. Note the lack of the Sphinx automodule and mock modules due to its focus on results reporting.

***
Git
***

* ``./.gitignore``
* ``./pyproject.toml``

The modsim template is intended to use `Git`_ :cite:`git` for version control: a ``.gitignore`` file is included in the
main template directory. By default, it includes file paths and extensions that are not expected to be tracked,
such as the ``build/`` directory, Abaqus and `Cubit`_ :cite:`cubit` journal files, and others.

This template utilizes `setuptools_scm`_ :cite:`setuptools_scm` to assist with version numbering using Git metadata. A
WIP tutorial on its usage can be found as part of the `setuptools_scm WAVES Tutorial`_.

******
PyTest
******

* ``modsim_package/tests/test_*.py``
* ``./pyproject.toml``

For unit testing, `pytest`_ :cite:`pytest` is implemented for the rectangle compression simulation. These tests can be
found in ``modsim_package/tests/``. The prepackaged tests currently include testing on inputs passed to argparse, mesh
convergence, and helper functions used for the rectangle compression. There are 13 tests in total. Tests can be run
using ``scons unit_testing``.

Within the ``pyproject.toml`` file, pytest configuration options are set to use the default Pytest options.