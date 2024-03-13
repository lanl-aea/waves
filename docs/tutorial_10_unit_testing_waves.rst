.. _tutorial_unit_testing_waves:

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
        $ waves fetch --overwrite --destination eabm_package tutorials/eabm_package/__init__.py
        WAVES fetch
        Destination directory: 'eabm_package'
        $ waves fetch --overwrite --destination eabm_package/abaqus 'tutorials/eabm_package/abaqus/*'
        WAVES fetch
        Destination directory: 'eabm_package/abaqus'
        $ waves fetch --overwrite --destination eabm_package/python 'tutorials/eabm_package/python/__init__.py' 'tutorials/eabm_package/python/rectangle_compression_nominal.py' 'tutorials/eabm_package/python/rectangle_compression_cartesian_product.py' 'tutorials/eabm_package/python/post_processing.py'
        WAVES fetch
        Destination directory: 'eabm_package/python'
        $ waves fetch --overwrite 'tutorials/tutorial_01_geometry' 'tutorials/tutorial_02_partition_mesh' 'tutorials/tutorial_03_solverprep' 'tutorials/tutorial_04_simulation' 'tutorials/tutorial_05_parameter_substitution' 'tutorials/tutorial_06_include_files' 'tutorials/tutorial_07_cartesian_product' 'tutorials/tutorial_08_data_extraction' 'tutorials/tutorial_09_post_processing'
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'
        $ waves fetch tutorials/tutorial_09_post_processing_SConstruct && mv tutorial_09_post_processing_SConstruct SConstruct
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'

**************
Unit test file
**************

4. In the ``waves-tutorials/eabm_package/python/tests`` directory, Create a new file named ``test_post_processing.py`` from the contents below

.. admonition:: waves-tutorials/eabm_package/python/tests/test_post_processing.py

    .. literalinclude:: tests_test_post_processing.py
        :language: Python
        :lineno-match:

In the ``test_post_processing.py`` file, you'll find a test implementation of a simple function within the
``post_processing.py`` module. However, the remaining functions delve into more complex territory which need advanced
techniques such as ``mocking``. These aspects are intentionally left as exercises for you, the reader, to explore and
master. For a deeper understanding of how mocking operates in Python, refer to `Unittest Mock`_ :cite:`unittest-mock`.

**********
SConscript
**********

5. In the ``waves-tutorials`` directory, Create a new file named ``unit_testing`` from the contents below

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

6. Update the ``SConstruct`` file. A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_post_processing_waves`
   is included below to help identify the changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_10_unit_testing_SConstruct
      :language: Python
      :diff: tutorials_tutorial_09_post_processing_SConstruct

Our test alias is initialized similarly to that of the workflow aliases. In order to clarify that the tests are not
part of a modsim workflow, the ``unit_testing`` call is made separately from the workflow loop.

*************
Build Targets
*************

7. Build the test results

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons unit_testing

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
