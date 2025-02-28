.. _tutorial_latin_hypercube:

############################
Tutorial 07: Latin Hypercube
############################

.. include:: wip_warning.txt

**********
References
**********

* |PROJECT| :ref:`parameter_generator_api` API: :meth:`waves.parameter_generators.LatinHypercube`
* `Xarray`_ and the `xarray dataset`_ :cite:`xarray,hoyer2017xarray`

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
        $ waves fetch --overwrite --tutorial 7 && mv tutorial_07_cartesian_product_SConstruct SConstruct
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'

4. Download and copy the ``tutorial_07_cartesian_product`` file to a new file named ``tutorial_07_latin_hypercube``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_07_cartesian_product && cp tutorial_07_cartesian_product tutorial_07_latin_hypercube
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

********************
Parameter Study File
********************

5. Create a new file ``modsim_package/python/rectangle_compression_latin_hypercube.py`` from the content below.

.. admonition:: waves-tutorials/modsim_package/python/rectangle_compression_latin_hypercube.py

   .. literalinclude:: python_rectangle_compression_latin_hypercube.py
      :language: Python

**********
SConscript
**********

A ``diff`` against the ``tutorial_07_cartesian_product`` file from :ref:`tutorial_cartesian_product` is included
below to help identify the differences between the two parameter generators.

.. note::

   Note that the ``kwargs`` variable sets a fixed seed for the random number generator. This is required to make the
   parameter set reproducible during SCons configuration. Without this seed, *every* call of ``scons`` will produce a
   complete and unique parameter study. This will result in the full workflow re-executing on every ``scons`` call.

   If a fixed seed is not acceptable, users may protect the parameter study generation with a command-line option or
   generate the parameter study manually and use the :meth:`waves.parameter_generators.CustomStudy` to instantiate the
   parameter study object.

.. admonition:: waves-tutorials/tutorial_07_latin_hypercube

   .. literalinclude:: tutorials_tutorial_07_latin_hypercube
      :language: Python
      :diff: tutorials_tutorial_07_cartesian_product

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_cartesian_product` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_07_latin_hypercube_SConstruct
      :language: Python
      :diff: tutorials_tutorial_07_cartesian_product_SConstruct

*************
Build Targets
*************

6. Build the new targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons tutorial_07_latin_hypercube --jobs=4

************
Output Files
************

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build/tutorial_07_latin_hypercube/parameter_set0/
   build/tutorial_07_latin_hypercube/parameter_set0/
   |-- abaqus.rpy
   |-- abaqus.rpy.1
   |-- abaqus.rpy.2
   |-- assembly.inp
   |-- boundary.inp
   |-- field_output.inp
   |-- history_output.inp
   |-- materials.inp
   |-- parts.inp
   |-- rectangle_compression.com
   |-- rectangle_compression.dat
   |-- rectangle_compression.inp
   |-- rectangle_compression.inp.in
   |-- rectangle_compression.msg
   |-- rectangle_compression.odb
   |-- rectangle_compression.prt
   |-- rectangle_compression.sta
   |-- rectangle_compression.stdout
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

   0 directories, 28 files

**********************
Workflow Visualization
**********************

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves visualize tutorial_07_latin_hypercube --output-file tutorial_07_latin_hypercube.png --width=36 --height=12 --exclude-list /usr/bin .stdout .jnl .prt .com .msg .dat .sta

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves visualize tutorial_07_latin_hypercube --output-file tutorial_07_latin_hypercube_set0.png --width=28 --height=6 --exclude-list /usr/bin .stdout .jnl .prt .com .msg .dat .sta --exclude-regex "set[1-9]"
