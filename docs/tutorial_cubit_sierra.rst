.. _tutorial_cubit_sierra:

######################
Tutorial: Cubit+Sierra
######################

.. warning::

   Most WAVES tutorials are used as system tests in the regression test suite to ensure that the tutorial files are
   up-to-date and functional. The sierra local submission *without* sbatch is part of the regression suite, but the
   sbatch submission behavior is not. If you run into problems running this tutorial, please contact the WAVES
   development team.

.. include:: tutorial_cubit_alternate.txt

**********
References
**********

* `Cubit`_: Python Interface :cite:`cubit`
* `Cubit`_: Importing Cubit into Python :cite:`cubit`
* `Sierra`_: Sierra/SolidMechanics User's Guide :cite:`sierra-user`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

.. include:: tutorial_directory_setup.txt

4. Create a new ``tutorial_cubit`` directory with the ``waves fetch`` command below

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --destination tutorial_cubit tutorials/tutorial_cubit
   $ ls tutorial_cubit
   modsim_package/  abaqus  cubit  SConstruct  sierra fierro

5. Make the new ``tutorial_cubit`` directory the current working directory

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ cd tutorial_cubit
   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_cubit
   $ ls
   modsim_package/  abaqus  cubit  SConstruct  sierra fierro

**********
SConscript
**********

Note that the ``tutorial_cubit`` directory has four SConscript files: ``cubit``, ``abaqus``, ``sierra``, and ``fierro``.
The ``cubit`` and ``sierra`` files are relevant to the current tutorial. The ``abaqus`` and ``fierro`` workflows are
described in the complementary :ref:`tutorial_cubit_abaqus` and :ref:`tutorial_cubit_fierro`.

6. Review the ``cubit`` and ``sierra`` tutorials and compare them against the :ref:`tutorial_simulation` files.

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

8. Create or review the Sierra input file from the contents below

.. admonition:: waves-tutorials/tutorial_cubit/modsim_package/sierra/rectangle_compression.i

   .. literalinclude:: sierra_rectangle_compression.i
      :lineno-match:

**********
SConstruct
**********

Note that Sierra requires a separate construction environment from the launching Conda environment. This is because
Sierra ships with a version of Python that conflicts with the launching Conda environment. You may need to update the
Sierra activation shell command according to the instructions on your local system.

.. include:: tutorial_cubit_SConstruct.txt

*************
Build Targets
*************

9. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials/tutorial_cubit
   $ scons sierra
   scons: Reading SConscript files ...
   Checking whether /apps/abaqus/Commands/abq2024 program exists.../apps/abaqus/Commands/abq2024
   Checking whether abq2024 program exists...no
   Checking whether /apps/Cubit-16.12/cubit program exists.../apps/Cubit-16.12/cubit
   Checking whether cubit program exists...no
   Checking whether sierra program exists.../projects/sierra/sierra5121/install/tools/sntools/engine/sierra
   scons: done reading SConscript files.
   scons: Building targets ...
   Copy("build/sierra/rectangle_compression.i", "modsim_package/sierra/rectangle_compression.i")
   cd /home/roppenheimer/waves-tutorials/tutorial_cubit/build/sierra && python /home/roppenheimer/waves-tutorials/tutorial_cubit/modsim_package/cubit/rectangle_geometry.py > rectangle_geometry.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_cubit/build/sierra && python /home/roppenheimer/waves-tutorials/tutorial_cubit/modsim_package/cubit/rectangle_partition.py > rectangle_partition.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_cubit/build/sierra && python /home/roppenheimer/waves-tutorials/tutorial_cubit/modsim_package/cubit/rectangle_mesh.py --element-type SHELL --solver sierra > rectangle_mesh.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_cubit/build/sierra && /projects/sierra/sierra5121/install/tools/sntools/engine/sierra adagio -i rectangle_compression.i > rectangle_compression.stdout 2>&1
   scons: done building targets.

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build/abaqus`` directory, as shown
below.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_cubit
   $ tree build/sierra/
   build/sierra/
   |-- rectangle_compression.e
   |-- rectangle_compression.i
   |-- rectangle_compression.log
   |-- rectangle_compression.stdout
   |-- rectangle_geometry.cub
   |-- rectangle_geometry.stdout
   |-- rectangle_mesh.cub
   |-- rectangle_mesh.g
   |-- rectangle_mesh.stdout
   |-- rectangle_partition.cub
   `-- rectangle_partition.stdout

   0 directories, 11 files
