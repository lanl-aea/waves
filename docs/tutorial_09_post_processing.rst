.. _tutorial_post_processing:

############################
Tutorial 09: Post-Processing
############################

.. _tutorial_post_processing_references:

**********
References
**********

* |PROJECT| :ref:`waves_scons_api` API: :meth:`waves.scons_extensions.python_builder_factory`
* |PROJECT| :ref:`parameter_generator_api` API: :meth:`waves.parameter_generators.CartesianProduct`
* `Xarray`_ and the `xarray dataset`_ :cite:`xarray,hoyer2017xarray`
* `pandas`_ :cite:`pandas`
* `matplotlib`_ :cite:`matplotlib`
* `Python generator expressions`_ :cite:`python-generator-expressions`

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
        $ waves fetch --overwrite --tutorial 8 && mv tutorial_08_data_extraction_SConstruct SConstruct
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'

4. Download and copy the ``tutorial_08_data_extraction`` file to a new file named ``tutorial_09_post_processing``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_08_data_extraction && cp tutorial_08_data_extraction tutorial_09_post_processing
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

**********
SConscript
**********

A ``diff`` against the ``tutorial_08_data_extraction`` file from :ref:`tutorial_data_extraction` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/tutorial_09_post_processing

   .. literalinclude:: tutorials_tutorial_09_post_processing
      :language: Python
      :diff: tutorials_tutorial_08_data_extraction

The Python 3 post-processing script is executed with the :meth:`waves.scons_extensions.python_builder_factory` builder
from the :class:`waves.scons_extensions.WAVESEnvironment` construction environment. This builder behaves similarly to
the :meth:`waves.scons_extensions.abaqus_journal_builder_factory` builders introduced in earlier tutorials. By default,
the builder uses the same Python interpreter as the launching `Conda`_ environment where `SCons`_ and WAVES are
installed. So unlike Abaqus Python, the user has full control over the Python execution environment.

Advanced `SCons`_ users may be tempted to write an `SCons Python function builder`_ for the post-processing task
:cite:`SCons`. A Python function builder would have the advantage of allowing users to pass Python objects to the task
definition directly. This would eliminate the need to read an intermediate YAML file for the plot selection dictionary,
for instance.

Here we use the ``post_processing.py`` CLI instead of the module's API for the task definition because the
post-processing will include plotting with `matplotlib`_ :cite:`matplotlib`, which is not thread-safe
:cite:`matplotlib-thread-safety`. When the CLI is used, multiple post-processing tasks from *separate* workflows can be
executed in parallel because each task will be launched from a separate Python main process. Care must still be taken to
ensure that the post-processing tasks do not write to the same files, however.

**********************
Post-processing script
**********************

5. In the ``waves-tutorials/modsim_package/python`` directory, create a file called ``post_processing.py`` using the
   contents below.

.. note::

   Depending on the memory and disk resources available and the size of the simulation workflow results, modsim projects
   may need to review the `Xarray`_ documentation for resource management specific to the projects' use case.

.. admonition:: waves-tutorials/modsim_package/python/post_processing.py

   .. literalinclude:: python_post_processing.py
      :language: Python

The post-processing script is the first Python 3 script introduced in the core tutorials. It differs from the Abaqus
journal files by executing against the Python 3 interpreter of the launching `Conda`_ environment where |PROJECT| is
installed. Unlike the Abaqus Python 2 environment used to execute journal files, users have direct control over this
environment and can use the full range of Python packages available with the `Conda`_ package manager.

Additionally, the full Python 3 environment allows greater flexibility in unit testing. The post-processing script has
been broken into small units of work for ease of testing, which will be introduced in :ref:`tutorial_unit_testing`.
Testing is important to verify that data manipulation is performed correctly. As an added benefit, writing small,
single-purpose functions makes project code more re-usable and the project can build a small library of common
utilities.

While it is possible to unit test Abaqus Python 2 scripts, most operations in the tutorial journal files require
operations on real geometry files, which requires system tests. :ref:`tutorial_regression_testing` will introduce
an example solution to performing system tests on simulation workflows.

Take some time to review the individual functions and their documentation, both in the source file and as rendered by
the documentation. Most of the behavior is explained in the :ref:`tutorial_post_processing_references` third-party
package documentation or the Python documentation. Most of the Python built-in operations should look familiar, but
novice Python users may be unfamiliar with the generator expression stored in the ``data_generator`` variable of the
``combine_data`` function. `Python generator expressions`_  behave similarly to list comprehensions. A generator
expression is used here to avoid performing file I/O operations until the post-processing script is ready to catenate
the results files into a single `xarray dataset`_.

The script API and CLI are included in the :ref:`waves_tutorial_api`: :ref:`post_processing_api` and
:ref:`waves_tutorial_cli`: :ref:`post_processing_cli`, respectively. Generally, this example script tries to model the
separation of: data input, data processing, data output, and status reporting. The `Software Carpentry: Python Novice`_
is a good introduction to Python programming practices :cite:`swc-python`.

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_data_extraction` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_09_post_processing_SConstruct
      :language: Python
      :diff: tutorials_tutorial_08_data_extraction_SConstruct

*************
Build Targets
*************

6. Build the new targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons tutorial_09_post_processing --jobs=4
   <output truncated>

************
Output Files
************

7. Observe the catenated parameter results and paramter study dataset in the post-processing task's STDOUT file

.. code-block::

   $ tree build/tutorial_09_post_processing/ -L 1
   build/tutorial_09_post_processing/
   |-- parameter_set0
   |-- parameter_set1
   |-- parameter_set2
   |-- parameter_set3
   |-- parameter_study.h5
   |-- stress_strain_comparison.csv
   |-- stress_strain_comparison.pdf
   `-- stress_strain_comparison.stdout

   4 directories, 4 files
   $ cat build/tutorial_09_post_processing/stress_strain_comparison.stdout
   <xarray.Dataset>
   Dimensions:             (step: 1, time: 5, elements: 1, integration point: 4,
                            E values: 4, set_name: 4, S values: 4)
   Coordinates:
     * step                (step) object 'Step-1'
     * time                (time) float64 0.0175 0.07094 0.2513 0.86 1.0
     * elements            (elements) int64 1
       integrationPoint    (elements, integration point) float64 1.0 nan nan nan
     * E values            (E values) object 'E11' 'E22' 'E33' 'E12'
     * S values            (S values) object 'S11' 'S22' 'S33' 'S12'
     * set_name            (set_name) <U14 'parameter_set0' ... 'parameter...
       set_hash            (set_name) object ...
   Dimensions without coordinates: integration point
   Data variables:
       E                   (set_name, step, time, elements, integration point, E values) float32 ...
       S                   (set_name, step, time, elements, integration point, S values) float32 ...
       displacement        (set_name) float64 ...
       global_seed         (set_name) float64 ...
       height              (set_name) float64 ...
       width               (set_name) float64 ...

The purpose of catenating the parameter set simulations with the parameter study definition is to examine the
connections between output quantities of interest as a function of the parameter study inputs. Working from a single
Xarray dataset makes sensitivity studies easier to conduct. In this tutorial, a qualitative comparison is provided in
the stress-strain comparison plot, where each parameter set is plotted as a separate series and identified in the
legend.

.. figure:: tutorial_09_post_processing_stress_strain_comparison.png
   :align: center
   :width: 50%

Note that in this example, most of the parameter sets are expected to overlap with differences as a function of the
geometric parameters. Review the parameter study introduced in :ref:`tutorial_cartesian_product` and the contents
of the `parameter_study.h5` file to identify the expected differences in the stress-strain response.

The :ref:`modsim_templates` provided by WAVES contain a similar parameter study for mesh convergence as a template for
new projects. The :ref:`waves_fetch_cli` subcommand may be used to recursively fetch directories or to fetch individual
files from both the :ref:`modsim_templates` and the tutorials.

**********************
Workflow Visualization
**********************

View the workflow directed graph by running the following command and opening the image in your preferred image viewer.
Plot the workflow with only the first set, ``set0``.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves visualize tutorial_09_post_processing --output-file tutorial_09_post_processing_set0.png --width=54 --height=8 --exclude-list /usr/bin .stdout .jnl .prt .com .msg .dat .sta --exclude-regex "set[1-9]"

The output should look similar to the figure below.

.. raw:: latex

    \begin{landscape}
        \vspace*{\fill}

.. figure:: tutorial_09_post_processing_set0.png
   :align: center
   :width: 100%

.. raw:: latex

        \vspace*{\fill}
    \end{landscape}

As in :ref:`tutorial_data_extraction`, the directed graph has not changed much. This tutorial adds the ``*.pdf`` plot
of stress vs. strain.
