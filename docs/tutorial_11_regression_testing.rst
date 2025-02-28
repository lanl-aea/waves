.. _tutorial_regression_testing:

###############################
Tutorial 11: Regression Testing
###############################

Regression testing is the practice of running a verification test suite after making changes to a repository or
codebase. For modsim repositories, there may not be many unit or integration tests if there is no software or scripting
library specific to the project. Instead, regression testing a modsim repository may look more like regular execution of
system tests that verify the simulation workflow still executes as expected.

Ideally, this verification suite of system tests would perform the complete simulation workflow from start to finish.
However, modsim repositories often contain simulations that are computationally expensive or produce large amounts of
data on disk. In these cases, it may be too expensive to run the full simulation suite at any regular interval. It is
still desirable to provide early warning of breaking changes in the simulation workflow, so as much of the workflow that
can be tested should be tested as regularly as possible given compute resource constraints.

This tutorial introduces a project wide alias to allow convenient execution of the simulation workflow through the
simulation datacheck task introduced in :ref:`tutorial_simulation`. From that tutorial onward, each tutorial has
propagated a tutorial specific datacheck alias. This tutorial will add a project wide ``datacheck`` alias and apply it
to a copy of the :ref:`tutorial_post_processing` configuration files. The user may also go back to previous
tutorials to include the full suite of datacheck tasks in the project wide datacheck regression test alias.

In addition to the datachecks, this tutorial will introduce a full simulation results regression test script and task.
The regression test task will be added to the regular workflow alias to run everytime the full workflow is run. This
test compares the actual simulation results within a float tolerance. Comprehensive results regression testing is
valuable to evaluate changes to important quantities of interest when software versions change, e.g. when installing a
new version of Abaqus.

After this tutorial, the workflow will have three sets of tests: fast running unit tests introduced in
:ref:`tutorial_unit_testing`, relatively fast running simulation preparation checks with the ``datacheck`` alias, and
full simulation results regression tests. The tutorial simulations run fast enough that performing the full suite of
tests for every change in the project is tractable. However, in practice, projects may choose to run only the unit tests
and datachecks on a per-change basis and reserve the comprehensive results testing for a scheduled regression suite.

**********
References
**********

* :ref:`testing`
* `SCons Alias`_ :cite:`scons-user`
* Continuous Integration software

  * GitHub Actions: https://docs.github.com/en/actions :cite:`github-actions`
  * Gitlab CI: https://docs.gitlab.com/ee/ci/ :cite:`gitlab-ci`
  * Bitbucket Pipelines: https://bitbucket.org/product/features/pipelines :cite:`bitbucket-pipelines`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

.. include:: version_check_warning.txt

*******************
Directory Structure
*******************

.. include:: tutorial_directory_setup.txt

.. note::

    If you skipped any of the previous tutorials, run the following commands to create a copy of the necessary tutorial
    files.

    .. code-block:: bash

        $ pwd
        /home/roppenheimer/waves-tutorials
        $ waves fetch --overwrite --tutorial 10 && mv tutorial_10_unit_testing_SConstruct SConstruct
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'

4. Download and copy the ``tutorial_09_post_processing`` file to a new file named ``tutorial_11_regression_testing``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_09_post_processing && cp tutorial_09_post_processing tutorial_11_regression_testing
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

*****************
Regression Script
*****************

5. In the ``waves-tutorials/modsim_package/python`` directory, review the file named ``regression.py`` introduced in
   :ref:`tutorial_unit_testing`.

.. admonition:: waves-tutorials/modsim_package/python/regression.py

   .. literalinclude:: python_regression.py
      :lineno-match:

********
CSV file
********

6. In the ``waves-tutorials/modsim_package/python`` directory, create a new file named
   ``rectangle_compression_cartesian_product.csv`` from the contents below

.. admonition:: waves-tutorials/modsim_package/python/rectangle_compression_cartesian_product.csv

   .. literalinclude:: python_rectangle_compression_cartesian_product.csv
      :lineno-match:

This file represents a copy of previous simulation results that the project has stored as the reviewed and approved
simulation results. The regression task will compare these "past" results with the current simulation results produced
during the post-processing task introduced in :ref:`tutorial_post_processing`
``rectangle_compression_cartesian_product.csv`` using the :ref:`regression_cli` CLI.

**********
SConscript
**********

A ``diff`` against the ``tutorial_09_post_processing`` file from :ref:`tutorial_post_processing` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/tutorial_11_regression_testing

   .. literalinclude:: tutorials_tutorial_11_regression_testing
      :language: Python
      :diff: tutorials_tutorial_09_post_processing

There are two changes made in this tutorial. The first is to compare the expected simulation results to the current
simulation's output. A new task compares the expected results as the CSV file created above against the current
simulation output with the new Python script, :ref:`regression_cli`. See the :ref:`regression_cli` CLI documentation for
a description of the post-processing script's behavior.

The second change adds a dedicated alias for the datacheck targets to allow partial workflow execution. This is useful
when a full simulation may take a long time, but the simulation preparation is worth testing on a regular basis. We've
also added the regression alias introduced briefly in :ref:`tutorial_unit_testing`. Previously, this alias was a
duplicate of the ``unit_testing`` workflow alias. Now this alias can be used as a collector alias for running a
regression suite with a single command, while preserving the ability to run the unit tests as a standalone workflow.

Here we add the datacheck targets as an example of running a partial workflow as part of the regression test suite. For
fast running simulations, it would be valuable to run the full simulation and post-processing with CSV results testing
as part of the regular regression suite. For large projects with long running simulations, several regression aliases
may be added to facilitate testing at different intervals. For instance, the datachecks might be run everytime the
project changes, but the simulations might be run on a weekly schedule with a ``regression_weekly`` alias that includes
the full simulations in addition to the unit tests and datachecks.

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_unit_testing` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_11_regression_testing_SConstruct
      :language: Python
      :diff: tutorials_tutorial_10_unit_testing_SConstruct

*************
Build Targets
*************

7. Build the datacheck targets without executing the full simulation workflow

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ time scons datacheck --jobs=4
   <output truncated>
   scons: done building targets.

   real 0m9.952s
   user 0m21.537s
   sys  0m15.664s

8. Run the full workflow and verify that the CSV regression test passes

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons datacheck --clean
   $ time scons tutorial_11_regression_testing --jobs=4
   <output truncated>
   scons: done building targets.

   real 0m29.031s
   user 0m25.712s
   sys  0m25.622s
   $ cat build/tutorial_11_regression_testing/regression.yaml
   CSV comparison: true

If you haven't added the project-wide datacheck alias to the previous tutorials, you should expect the ``datacheck``
alias to run faster than the ``tutorial_11_regression_testing`` alias because the datacheck excludes the solve, extract,
and post-processing tasks. In these tutorials, the difference in execution time is not large. However, in many
production modsim projects, the simulations may require hours or even days to complete. In that case, the relatively
fast running solverprep verification may be tractable for regular testing where the full simulations and post-processing
are not.

To approximate the time savings of the new project-wide ``datacheck`` alias for a (slightly) larger modsim project, you
can go back through the previous tutorials and add each tutorial's datacheck task to the new alias. For a fair
comparison, you will also need to add a comparable alias to collect the full workflow for each tutorial, e.g.
``full_workflows``. You can then repeat the ``time`` commands above with a more comprehensive ``datacheck`` and
``full_workflows`` aliases.

************
Output Files
************

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build/tutorial_11_regression_testing/parameter_set0/
   build/tutorial_11_regression_testing/parameter_set0/
   |-- abaqus.rpy
   |-- abaqus.rpy.1
   |-- abaqus.rpy.2
   |-- assembly.inp
   |-- boundary.inp
   |-- field_output.inp
   |-- history_output.inp
   |-- materials.inp
   |-- parts.inp
   |-- rectangle_compression.inp
   |-- rectangle_compression.inp.in
   |-- rectangle_compression_DATACHECK.023
   |-- rectangle_compression_DATACHECK.com
   |-- rectangle_compression_DATACHECK.dat
   |-- rectangle_compression_DATACHECK.mdl
   |-- rectangle_compression_DATACHECK.msg
   |-- rectangle_compression_DATACHECK.odb
   |-- rectangle_compression_DATACHECK.prt
   |-- rectangle_compression_DATACHECK.sim
   |-- rectangle_compression_DATACHECK.stdout
   |-- rectangle_compression_DATACHECK.stt
   |-- rectangle_geometry.cae
   |-- rectangle_geometry.jnl
   |-- rectangle_geometry.stdout
   |-- rectangle_mesh.cae
   |-- rectangle_mesh.inp
   |-- rectangle_mesh.jnl
   |-- rectangle_mesh.stdout
   |-- rectangle_partition.cae
   |-- rectangle_partition.jnl
   `-- rectangle_partition.stdout

   0 directories, 31 files
   $ tree build/tutorial_11_regression_testing/ -L 1
   build/tutorial_11_regression_testing/
   |-- parameter_set0
   |-- parameter_set1
   |-- parameter_set2
   |-- parameter_set3
   |-- parameter_study.h5
   |-- regression.yaml
   |-- regression.yaml.stdout
   |-- stress_strain_comparison.csv
   |-- stress_strain_comparison.pdf
   `-- stress_strain_comparison.stdout

   4 directories, 6 files

**********************
Workflow Visualization
**********************

View the workflow directed graph by running the following command and opening the image in your preferred image viewer.
Plot the workflow with only the first set, ``set0``.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves visualize datacheck --output-file tutorial_11_datacheck_set0.png --width=42 --height=8 --exclude-list /usr/bin .stdout .jnl .prt .com .msg .dat .sta --exclude-regex "set[1-9]"

The output should look similar to the figure below.

.. raw:: latex

    \begin{landscape}
        \vspace*{\fill}

.. figure:: tutorial_11_datacheck_set0.png
   :align: center
   :width: 100%

.. raw:: latex

        \vspace*{\fill}
    \end{landscape}

This tutorial's ``datacheck`` directed graph should look different from the graph in
:ref:`tutorial_post_processing`. Here we have plotted the ``datacheck`` alias output, which does not execute the
full simulation workflow. This partial directed graph may run faster than the full simulation workflow for frequent
regression tests.

**********
Automation
**********

There are many tools that can help automate the execution of the modsim project regression tests. With the collector
alias, those tools need only execute a single `SCons`_ command to perform the selected, lower cost tasks for simulation
workflow verification, ``scons datacheck``. If `git`_ :cite:`git` is used as the version control system, developer
operations software such as `GitHub`_ :cite:`github`, `Gitlab`_ :cite:`gitlab`, and Atlassian's `Bitbucket`_
:cite:`bitbucket` provide continuous integration software that can automate verification tests on triggers, such as
merge requests, or on a regular schedule.

.. TODO: template .gitlab-ci.yml file
.. TODO: add references to alternative to gitlab
