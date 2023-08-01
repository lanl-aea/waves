.. _tutorial_cubit_sierra:

######################
Tutorial: Cubit+Sierra
######################

**********
References
**********

* `Cubit`_: Python Interface :cite:`cubit`
* `Cubit`_: Importing Cubit into Python :cite:`cubit`
* `Sierra`_: Sierra/SolidMechanics User's Guide :cite:`sierra-user`

***********
Environment
***********

.. only:: aea

   .. note::

      This tutorial requires Sierra to be installed and available on ``PATH``. On AEA servers, you can make Sierra
      available with the following command.

      .. code-block::

         module use /projects/aea_compute/modulefiles
         module load sierra

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Create a new ``tutorial_cubit`` directory with the ``waves fetch`` command below

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials
   $ waves fetch tutorials/tutorial_cubit --destination tutorial_cubit
   $ ls tutorial_cubit
   eabm_package/  abaqus  cubit  SConstruct  sierra

4. Make the new ``tutorial_cubit`` directory the current working directory

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials
   $ cd tutorial_cubit
   $ pwd
   /path/to/waves-tutorials/tutorial_cubit
   $ ls
   eabm_package/  abaqus  cubit  SConstruct  sierra

**********
SConscript
**********

Note that the ``tutorial_cubit`` directory has three SConscript files: ``cubit``, ``abaqus``, ``sierra``. The first and
last are relevant to the current tutorial. The ``abaqus`` workflow is described in the complementary
:ref:`tutorial_cubit_abaqus`.

5. Review the ``cubit`` and ``sierra`` tutorials and compare them against the :ref:`tutorial_simulation_waves` files.

The structure has changed enough that a diff view is not as useful. Instead the contents of the new SConscript files are
duplicated below.

.. admonition:: waves-tutorials/tutorial_cubit/cubit

   .. literalinclude:: tutorial_cubit_cubit
      :language: Python
      :lineno-match:

.. admonition:: waves-tutorials/tutorial_cubit/sierra

   .. literalinclude:: tutorial_cubit_sierra
      :language: Python
      :lineno-match:

*******************
Cubit Journal Files
*******************

.. include:: tutorial_cubit_journal_files.txt

********************
Sierra Input File(s)
********************

7. Create or review the Sierra input file from the contents below

.. admonition:: waves-tutorials/tutorial_cubit/eabm_package/sierra/rectangle_compression.i

   .. literalinclude:: sierra_rectangle_compression.i
      :lineno-match:

**********
SConstruct
**********

.. include:: tutorial_cubit_SConstruct.txt

*************
Build Targets
*************

8. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials/tutorial_cubit
   $ scons sierra
   scons: Reading SConscript files ...
   Checking whether abq2023 program exists.../apps/abaqus/Commands/abq2023
   Checking whether cubit program exists.../apps/Cubit-15.8/cubit
   scons: done reading SConscript files.
   scons: Building targets ...

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build/abaqus`` directory, as shown
below.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_cubit
   $ tree build/sierra
   build/sierra
   |-- assembly.inp
   |-- boundary.inp
   |-- field_output.inp
   |-- history_output.inp
   |-- materials.inp
   |-- parts.inp
   |-- rectangle_compression.abaqus_v6.env
   |-- rectangle_compression.com
   |-- rectangle_compression.dat
   |-- rectangle_compression.inp
   |-- rectangle_compression.msg
   |-- rectangle_compression.odb
   |-- rectangle_compression.prt
   |-- rectangle_compression.sta
   |-- rectangle_compression.stdout
   |-- rectangle_geometry.cub
   |-- rectangle_geometry.stdout
   |-- rectangle_mesh.cub
   |-- rectangle_mesh.inp
   |-- rectangle_mesh.stdout
   |-- rectangle_partition.cub
   `-- rectangle_partition.stdout

   0 directories, 22 files
