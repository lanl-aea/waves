.. _tutorial_unit_testing:

#########################
Tutorial 10: Unit Testing
#########################

Unit testing is a software development practice that allows developers to verify the functionality of individual units
or components of their codebase. In modsim repositories, unit tests play a vital role in verifying custom scripting
libraries tailored to the project. This tutorial introduces a project-wide alias, streamlining the execution of unit
tests using the `pytest`_ :cite:`pytest` framework.

**********
References
**********

* `pytest`_ :cite:`pytest`
* :ref:`testing`

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
        $ waves fetch --overwrite --tutorial 9 && mv tutorial_09_post_processing_SConstruct SConstruct
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'

*****************
Regression Script
*****************

4. In the ``waves-tutorials/modsim_package/python`` directory, create a new file named ``regression.py`` from the
   contents below

.. admonition:: waves-tutorials/modsim_package/python/regression.py

   .. literalinclude:: python_regression.py
      :lineno-match:

This script is introduced early for :ref:`tutorial_regression_testing` because unit testing the
:ref:`post_processing_cli` functions requires advanced testing techniques. The functions of :ref:`regression_cli` can be
tested more directly as an introduction to Python unit testing.

**************
Unit test file
**************

5. In the ``waves-tutorials/modsim_package/python/tests`` directory, Create a new file named ``test_regression.py`` from the contents below

.. admonition:: waves-tutorials/modsim_package/python/tests/test_regression.py

    .. literalinclude:: tests_test_regression.py
        :language: Python
        :lineno-match:

In the ``test_regression.py`` file, you'll find a test implementation of two simple functions within the
``regression.py`` module. However, the remaining functions delve into more complex territory which need advanced
techniques such as ``mocking``. These aspects are intentionally left as exercises for you, the reader, to explore and
master. For a deeper understanding of how mocking operates in Python, refer to `Unittest Mock`_ :cite:`unittest-mock`. A
more complete suite of unit tests may be found in the :ref:`modsim_templates`.

**********
SConscript
**********

6. In the ``waves-tutorials`` directory, create a new file named ``unit_testing`` from the contents below

.. admonition:: waves-tutorials/unit_testing

    .. literalinclude:: tutorials_unit_testing
        :language: Python
        :lineno-match:

For this SCons task, the primary purpose of the `pytest JUnit XML output`_ report is to provide SCons with a build
target to track. If the project uses a continuous integration server, the output may be used for automated test
reporting :cite:`pytest-junitxml`.

**********
SConstruct
**********

7. Update the ``SConstruct`` file. A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_post_processing`
   is included below to help identify the changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_10_unit_testing_SConstruct
      :language: Python
      :diff: tutorials_tutorial_09_post_processing_SConstruct

Our test alias is initialized similarly to that of the workflow aliases. In order to clarify that the tests are not
part of a modsim workflow, the ``unit_testing`` call is made separately from the workflow loop. Additionally, a
regression test alias is added as a collector alias for future expansion beyond the unit tests in
:ref:`tutorial_regression_testing`.

*************
Build Targets
*************

8. Build the test results

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons unit_testing
   <output truncated>

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below. Note that the output files from the previous tutorials may also exist in the ``build`` directory, but the
directory is specified by name to reduce clutter in the output shown.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build/unit_testing/
   build/unit_testing/
   └── unit_testing_results.xml

   0 directories, 1 file
