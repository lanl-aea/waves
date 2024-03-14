.. _modsim_templates:

################
ModSim Templates
################

.. include:: modsim_templates.txt

*************
Prerequisites
*************

.. include:: tutorial_00_prerequisites.txt

In addition to the tutorial prerequisites, the modsim template implements documentation with `Sphinx`_. The Sphinx
tutorial below is a good introduction to writing documentation with `reStructuredText`_ :cite:`rst`. The Sphinx
documentation also contains a useful reference in the `reStructuredText Primer`_ :cite:`sphinx`.

4. `Sphinx`_ tutorial: https://www.sphinx-doc.org/en/master/tutorial/index.html :cite:`sphinx,sphinx-tutorial`

There is one significant difference between the Sphinx tutorial and the modsim template project. The Sphinx tutorial and
Sphinx documentation assumes that users are building documentation with `GNU Make`_ :cite:`gnu-make`. Since the modsim
template and WAVES already use the `SCons`_ :cite:`SCons` build system for running workflows, the documentation template
files also use SCons as the build system. Users can find the available documentation commands with ``scons -h`` and the
documentation configuration is found in the ``modsim_template/docs/SConscript`` file, which should look familiar to
SCons users but may require some translation from the Sphinx manual build commands.

********************
Fetch Template Files
********************

See the :ref:`waves_fetch_cli` subcommand for a complete discussion of behavior and options. The examples below are
included as a recommended starting place when creating a modsim project from scratch. This will create a complete and
functional modsim project in the user's home directory. If the directory already exists and is populated, existing files
will *not* be overwritten.

.. code-block::

   $ waves fetch modsim_template --destination ~/modsim_template

You can view the list of available files as below.

.. code-block::

   $ waves fetch --print-available

In addition to the modsim template files, the subcommand can also fetch all of the tutorial files, so the list may be
quite long. To view a shorter list, or to preview the file copy operations prior to execution, use the following option

.. code-block::

   $ waves fetch modsim_template --destination ~/modsim_template --dry-run

***************
Version Control
***************

The modsim template in this project does not require users to implement version control, but version control is highly
recommended. The purpose and benefits of using version control for modsim files can be found in the
:ref:`computational_tools` :ref:`version_control` discussion. The modsim template can be updated to use dynamic
versioning with the :ref:`tutorial_setuptools_scm`, where `setuptools_scm`_ :cite:`setuptools_scm` is a software
package that can retrieve a project version number from version control software, such as `git`_ :cite:`git`.
