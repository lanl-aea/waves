.. _tutorial_unit_testing_waves:

######################
Tutorial: Unit Testing
######################

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
        $ waves fetch tutorials/tutorial_09_post_processing_SConstruct && mv tutorial_09_post_processing_SConstruct SConstruct
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'

4. Create testing initialization files for the testing directory.

.. admonition:: waves-tutorials/eabm_package/python/tests/__init__.py

   .. code-block::

      $ pwd
      /home/roppenheimer/waves-tutorials
      $ mkdir eabm_package/python/tests
      $ touch eabm_package/python/tests/__init__.py

**************
Unit test file
**************

5. In the ``waves-tutorials/eabm_package/python/tests`` directory, Create a new file named ``test_post_processing.py`` from the contents below

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

6. In the ``waves-tutorials`` directory, Create a new file named ``unit_testing`` from the contents below

.. admonition:: waves-tutorials/unit_testing

    .. literalinclude:: tutorials_unit_testing
        :language: Python
        :lineno-match:

This ``SConscript`` file will run all tests found in the ``test_files`` list. The ``unittest_command`` uses the
``--junitxml`` argument to generate JUnit XML reports. The purpose of JUnit XML reports are to provide ``SCons`` with a
build target that we can track.

**********
SConstruct
**********

8. Update the ``SConstruct`` file. A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_post_processing_waves`
is included below to help identify the changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_unit_testing_SConstruct
      :language: Python
      :diff: tutorials_tutorial_09_post_processing_SConstruct

Our test alias is initialized similarly to that of the workflow aliases. In order to show that the tests
themselves are not a modsim workflow and not tied to any specific workflow file, we have moved the ``unit_testing``
call to a separate section.

*************
Build Targets
*************

9. Build the test results

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons unit_testing

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below. Note that the output files from the previous tutorials also exist in the ``build`` directory, but the directory
is specified by name to reduce clutter in the output shown.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build/unit_testing/
   build/unit_testing/
   └── unit_testing_results.xml

   0 directories, 1 file
