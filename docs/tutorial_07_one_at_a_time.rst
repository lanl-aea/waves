.. _tutorial_one_at_a_time:

##########################
Tutorial 07: One-at-a-Time
##########################

.. include:: wip_warning.txt

**********
References
**********

* |PROJECT| :ref:`parameter_generator_api` API: :meth:`waves.parameter_generators.OneAtATime`
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

4. Download and copy the ``tutorial_07_cartesian_product`` file to a new file named ``tutorial_07_one_at_a_time``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_07_cartesian_product && cp tutorial_07_cartesian_product tutorial_07_one_at_a_time
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

********************
Parameter Study File
********************

In this tutorial, we will use the previous parameter study python file used in :ref:`tutorial_cartesian_product` to
define the parameter study.

In the ``parameter_schema``, there are two parameters with two samples each and two parameters with one sample
each. The nominal parameter set is constructed from the first sample of each parameter. This will result in three total
simulations: one for the nominal parameter set and two using each off-nominal value.

The idea behind one-at-a-time parameter sets is that, for each parameter set, only one value of one single parameter has
changed compared to the nominal values.

**********
SConscript
**********

5. Modify the SConscript file ``tutorial_07_one_at_a_time`` to utilize the :meth:`waves.parameter_generators.OneAtATime`
builder.

A ``diff`` against the ``tutorial_07_cartesian_product`` file from :ref:`tutorial_cartesian_product` is included
below to help identify the differences between the two parameter generators.

.. admonition:: waves-tutorials/tutorial_07_one_at_a_time

   .. literalinclude:: tutorials_tutorial_07_one_at_a_time
      :language: Python
      :diff: tutorials_tutorial_07_cartesian_product

**********
SConstruct
**********

6. Add the workflow ``tutorial_07_one_at_a_time`` to the SConstruct file.

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_cartesian_product` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_07_one_at_a_time_SConstruct
      :language: Python
      :diff: tutorials_tutorial_07_cartesian_product_SConstruct

*************
Build Targets
*************

7. Build the new targets.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons tutorial_07_one_at_a_time --jobs=3

************
Output Files
************

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ tree build/tutorial_07_one_at_a_time/parameter_set0/
   build/tutorial_07_one_at_a_time/parameter_set0/
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
   $ waves visualize tutorial_07_one_at_a_time --output-file tutorial_07_one_at_a_time.png --width=36 --height=12 --exclude-list /usr/bin .stdout .jnl .prt .com .msg .dat .sta

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves visualize tutorial_07_one_at_a_time --output-file tutorial_07_one_at_a_time_set0.png --width=28 --height=6 --exclude-list /usr/bin .stdout .jnl .prt .com .msg .dat .sta --exclude-regex "set[1-9]"
