.. _modsim_templates:

################
ModSim Templates
################

.. include:: modsim_templates.txt

*************
Prerequisites
*************

.. include:: tutorial_00_prerequisites.txt

In addition to the tutorial prerequisites, the modsim templates implement documentation with `Sphinx`_. The Sphinx
tutorial below is a good introduction to writing documentation with `reStructuredText`_ :cite:`rst`. The Sphinx
documentation also contains a useful reference in the `reStructuredText Primer`_ :cite:`sphinx`.

4. `Sphinx`_ tutorial: https://www.sphinx-doc.org/en/master/tutorial/index.html :cite:`sphinx,sphinx-tutorial`

There is one significant difference between the Sphinx tutorial and the modsim templates documentation. The Sphinx
tutorial and Sphinx documentation assumes that users are building documentation with `GNU Make`_ :cite:`gnu-make`. Since
the modsim templates and |PROJECT| already use the `SCons`_ :cite:`SCons` build system for running workflows, the
documentation template files also use SCons as the build system. Users can find the available documentation commands
with ``scons -h`` and the documentation configuration is found in the ``modsim_template/docs/SConscript`` file, which
should look familiar to SCons users but may require some translation from the Sphinx manual build commands.

********************
Template comparisons
********************

There are currently two template projects available: ``modsim_template`` and ``modsim_template_2``. The first
``modsim_template`` is most similar to the tutorials and will be the easiest starting point for novice SCons and
|PROJECT| users. It allows for a great deal of flexibility in both source and build tree structure. The second
``modsim_template_2`` has advantages for advanced SCons and |PROJECT| users but places restrictions on the source and
build tree structures and may be difficult for novice command line users to navigate.

``modsim_template_2`` uses the `SCons SConscript`_ ``duplicate=True`` default behavior :cite:`SCons,scons-user` to
reduce the number of explicit file copy operations with :meth:`waves.scons_extensions.copy_substfile` and the Abaqus
input file scanner, :meth:`waves.scons_extensions.abaqus_input_scanner`, to reduce the size of Abaqus solver source file
lists. This template also uses the :meth:`waves.scons_extensions.parameter_study_sconscript`` call to further reduce
task duplication. These features help reduce SConstruct and SConscript verbosity and aid in automated source list
construction.

However, these advanced features restrict source and/or build tree structure. The ``duplicate=True`` and
:meth:`waves.scons_extensions.abaqus_input_scanner` features require that the SConscript files must be co-located with
the source files they describe. Therefore, the part and simulation SConscript files (``rectangle`` and
``rectangle_compression``) are found in the ``modsim_package`` directory in ``modsim_template_2``.

The :meth:`scons_extensions.parameter_study_sconscript` feature allows projects to unpack parameter studies during an
SConscript call. This removes the need for separate ``nominal`` and ``mesh_convergence`` simulation workflow files,
which are replaced by a single ``rectangle_compression`` workflow file. Combining these simulation workflows reduces new
simulation definitions to an entry in SConstruct, but does require that workflow specific post-processing tasks be moved
to dedicated SConscript files: ``rectangle_compression-nominal-regression`` and
``rectangle_compression-mesh_convergence-post_processing``.

To preserve the build tree structure with nested SConscript calls, all SConscript files must be found in the same parent
directory, so the downstream workflow SConscript files (``rectangle_compression-nominal-regression`` and
``rectangle_compression-mesh_convergence-post_processing``) must also be located in the ``modsim_package`` directory.
This template requires a totally flat ``modsim_package`` structure, which may be cumbersome for large projects,
particularly if users tend to rely on graphical file browsers.

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

##################
External Resources
##################

.. include:: external_resources.txt