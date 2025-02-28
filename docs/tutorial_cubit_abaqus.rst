.. _tutorial_cubit_abaqus:

######################
Tutorial: Cubit+Abaqus
######################

This tutorial implements the same workflow introduced in :ref:`tutorial_simulation`, but uses `Cubit`_
:cite:`cubit` for the geometry, partition, and meshing tasks. It is included as an example for how to use `Cubit`_ with
a build system and include best practices, such as an API and CLI.

.. include:: tutorial_cubit_alternate.txt

**********
References
**********

* `Cubit`_: Python Interface :cite:`cubit`
* `Cubit`_: Importing Cubit into Python :cite:`cubit`
* `SCons Appendix D`_: ``AddPostAction`` :cite:`scons-user`
* `GNU sed`_ and `conda-forge sed`_ :cite:`gnu-sed`

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
   modsim_package/  abaqus  cubit  SConstruct  sierra

5. Make the new ``tutorial_cubit`` directory the current working directory

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ cd tutorial_cubit
   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_cubit
   $ ls
   modsim_package/  abaqus  cubit  SConstruct  sierra

.. _tutorials_tutorial_cubit:

**********
SConscript
**********

Note that the ``tutorial_cubit`` directory has three SConscript files: ``cubit``, ``abaqus``, ``sierra``. The first two
are relevant to the current tutorial. The ``sierra`` workflow is described in the complementary
:ref:`tutorial_cubit_sierra`.

6. Review the ``cubit`` and ``abaqus`` tutorials and compare them against the :ref:`tutorial_simulation` files.

The structure has changed enough that a diff view is not as useful. Instead the contents of the new SConscript files are
duplicated below.

.. admonition:: waves-tutorials/tutorial_cubit/cubit

   .. literalinclude:: tutorial_cubit_cubit
      :language: Python
      :lineno-match:

.. admonition:: waves-tutorials/tutorial_cubit/abaqus

   .. literalinclude:: tutorial_cubit_abaqus
      :language: Python
      :lineno-match:

Note that Cubit does not support the Abaqus plane stress element ``CPS4``, so we must add a post-action to the orphan
mesh target to change the element type. A post-action is used to avoid generating intermediate target files, which would
be required if we created a separate task for the file modification. This post-action is written to apply to a list, so
if additional orphan mesh files needed the same modification, the post-action would be added to each targets' build
signature definition with a single ``AddPostAction`` definition.

The ``sed`` command is not available on all systems, but a `Conda`_ packaged version, `conda-forge sed`_, of the `GNU
sed`_ program can be used to provide system-to-system consistency with `Conda environment management`_. See the `Conda`_
documentation for more information about virtual environment management with `Conda`_.

*******************
Cubit Journal Files
*******************

.. include:: tutorial_cubit_journal_files.txt

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
   /home/roppenheimer/waves-tutorials/tutorial_cubit
   $ scons abaqus
   scons: Reading SConscript files ...
   Checking whether /apps/abaqus/Commands/abq2024 program exists.../apps/abaqus/Commands/abq2024
   Checking whether abq2024 program exists...no
   Checking whether /apps/Cubit-16.12/cubit program exists.../apps/Cubit-16.12/cubit
   Checking whether cubit program exists...no
   Checking whether sierra program exists...no
   scons: done reading SConscript files.
   scons: Building targets ...
   Copy("build/abaqus/rectangle_compression.inp", "modsim_package/abaqus/rectangle_compression.inp")
   Copy("build/abaqus/assembly.inp", "modsim_package/abaqus/assembly.inp")
   Copy("build/abaqus/boundary.inp", "modsim_package/abaqus/boundary.inp")
   Copy("build/abaqus/field_output.inp", "modsim_package/abaqus/field_output.inp")
   Copy("build/abaqus/materials.inp", "modsim_package/abaqus/materials.inp")
   Copy("build/abaqus/parts.inp", "modsim_package/abaqus/parts.inp")
   Copy("build/abaqus/history_output.inp", "modsim_package/abaqus/history_output.inp")
   cd /home/roppenheimer/waves-tutorials/tutorial_cubit/build/abaqus && python /home/roppenheimer/waves-tutorials/tutorial_cubit/modsim_package/cubit/rectangle_geometry.py > rectangle_geometry.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_cubit/build/abaqus && python /home/roppenheimer/waves-tutorials/tutorial_cubit/modsim_package/cubit/rectangle_partition.py > rectangle_partition.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_cubit/build/abaqus && python /home/roppenheimer/waves-tutorials/tutorial_cubit/modsim_package/cubit/rectangle_mesh.py > rectangle_mesh.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_cubit/build/abaqus && /apps/abaqus/Commands/abq2024 -job rectangle_compression -input rectangle_compression -double both -interactive -ask_delete no > rectangle_compression.stdout 2>&1
   scons: done building targets.

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build/abaqus`` directory, as shown
below.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_cubit
   $ tree build/abaqus
   build/abaqus
   |-- assembly.inp
   |-- boundary.inp
   |-- field_output.inp
   |-- history_output.inp
   |-- materials.inp
   |-- parts.inp
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

   0 directories, 21 files
