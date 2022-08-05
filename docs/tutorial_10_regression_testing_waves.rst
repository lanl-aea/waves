.. _tutorial_regression_testing_waves:

###############################
Tutorial 10: Regression Testing
###############################

.. include:: wip_warning.txt

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
simulation datacheck task introduced in :ref:`tutorial_simulation_waves`. From that tutorial onward, each tutorial has
propagated a tutorial specific datacheck alias. This tutorial will add a project wide ``datacheck`` alias and apply it
to a copy of the :ref:`tutorial_post_processing` configuration files. The user may also go back to previous tutorials to
include the full suite of datacheck tasks in the project wide datacheck regression alias.

**********
References
**********

* :ref:`testing`
* Gitlab CI: https://docs.gitlab.com/ee/ci/ :cite:`gitlab-ci`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Create a directory ``tutorial_10_regression_testing`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir tutorial_10_regression_testing

4. Copy the ``tutorial_09_post_processing/SConscript`` file into the newly created ``tutorial_10_regression_testing``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_09_post_processing/SConscript tutorial_10_regression_testing/

**********
SConscript
**********

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_post_processing_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_10_regression_testing/SConscript

   .. literalinclude:: tutorial_10_regression_testing_SConscript
      :language: Python
      :diff: tutorial_09_post_processing_SConscript

To see the full power of the new project-wide ``datacheck`` alias, go back through the previous tutorials and add each
simulation specific datacheck task to the new alias.

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_include_files_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_10_regression_testing_SConstruct
      :language: Python
      :diff: eabm_tutorial_09_post_processing_SConstruct

*************
Build Targets
*************

5. Build the datacheck targets without executing the full simulation workflow

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons datacheck --jobs=4

************
Output Files
************
