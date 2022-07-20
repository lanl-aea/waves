.. _tutorial_cubit_waves:

##########################
Tutorial Cubit: Simulation
##########################

This tutorial implements the same workflow introduced in :ref:`tutorial_simulation_waves`, but uses `Cubit`_ for the
geometry, partition, and meshing tasks. It is included as an example for how to use `Cubit`_ with a build system and
include best practices, such as an API and CLI.

**********
References
**********

* `Cubit`_: Importing Cubit into Python

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Create directories ``tutorial_cubit`` and ``eabm_package/cubit`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir -p tutorial_cubit eabm_package_cubit

4. Copy the ``tutorial_04_simulation/SConscript`` file into the newly created ``tutorial_cubit``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_04_simulation/SConscript tutorial_cubit/

.. _tutorial_cubit_waves_SConscript:

**********
SConscript
**********

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_cubit/SConscript

   .. literalinclude:: tutorial_cubit_SConscript
      :language: Python
      :diff: tutorial_04_simulation_SConscript

*******************
Cubit Journal Files
*******************

5. Create the following journal files in the ``waves-eabm/eabm_package/cubit`` directory.

The Cubit journal files include the same CLI introduced in :ref:`tutorial_partition_mesh_waves` for the Abaqus journal
files. Besides the differences in Abaqus and Cubit commands, the major difference between the Abaqus and Cubit journal
files is the opportunity to use Python 3 with Cubit, where Abaqus journal files must use the Abaqus controlled
installation of Python 2. The API and CLI built from the Cubit journal files' docstrings may be found in the
:ref:`sphinx_api` for :ref:`cubit_journal_api` and the :ref:`sphinx_cli` for :ref:`cubit_journal_cli`, respectively.

.. admonition:: waves-eabm-tutorial/eabm_package/cubit/single_element_geometry.py

   .. literalinclude:: cubit_single_element_geometry.py
       :language: Python
       :lineno-match:

.. admonition:: waves-eabm-tutorial/eabm_package/cubit/single_element_partition.py

   .. literalinclude:: cubit_single_element_partition.py
       :language: Python
       :lineno-match:

.. admonition:: waves-eabm-tutorial/eabm_package/cubit/single_element_mesh.py

   .. literalinclude:: cubit_single_element_mesh.py
       :language: Python
       :lineno-match:

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_simulation_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_cubit_SConstruct
      :language: Python
      :diff: eabm_tutorial_04_simulation_SConstruct

*************
Build Targets
*************

6. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_cubit
    scons: Reading SConscript files ...
    Checking whether abaqus program exists.../apps/abaqus/Commands/abaqus
    scons: done reading SConscript files.
    scons: Building targets ...
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_cubit && /apps/abaqus/Commands/abaqus -information environment
    > single_element_geometry.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_cubit && /apps/abaqus/Commands/abaqus cae -noGui
    /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_geometry.py -- > single_element_geometry.stdout 2>&1
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_cubit && /apps/abaqus/Commands/abaqus -information
    environment > single_element_partition.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_cubit && /apps/abaqus/Commands/abaqus cae -noGui
    /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_partition.py -- > single_element_partition.stdout 2>&1
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_cubit && /apps/abaqus/Commands/abaqus -information environment
    > single_element_mesh.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_cubit && /apps/abaqus/Commands/abaqus cae -noGui
    /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_mesh.py -- > single_element_mesh.stdout 2>&1
    Copy("build/tutorial_cubit/single_element_compression.inp",
    "eabm_package/abaqus/single_element_compression.inp")
    Copy("build/tutorial_cubit/amplitudes.inp", "eabm_package/abaqus/amplitudes.inp")
    Copy("build/tutorial_cubit/assembly.inp", "eabm_package/abaqus/assembly.inp")
    Copy("build/tutorial_cubit/boundary.inp", "eabm_package/abaqus/boundary.inp")
    Copy("build/tutorial_cubit/field_output.inp", "eabm_package/abaqus/field_output.inp")
    Copy("build/tutorial_cubit/materials.inp", "eabm_package/abaqus/materials.inp")
    Copy("build/tutorial_cubit/parts.inp", "eabm_package/abaqus/parts.inp")
    Copy("build/tutorial_cubit/history_output.inp", "eabm_package/abaqus/history_output.inp")
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_cubit && /apps/abaqus/Commands/abaqus -information environment
    > single_element_compression_DATACHECK.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_cubit && /apps/abaqus/Commands/abaqus -job
    single_element_compression_DATACHECK -input single_element_compression -double both -datacheck -interactive -ask_delete
    no > single_element_compression_DATACHECK.stdout 2>&1
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_cubit && /apps/abaqus/Commands/abaqus -information environment
    > single_element_compression.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_cubit && /apps/abaqus/Commands/abaqus -job
    single_element_compression -input single_element_compression -double both -interactive -ask_delete no >
    single_element_compression.stdout 2>&1
    scons: done building targets.

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below. Note that the output files from the previous tutorials also exist in the ``build`` directory, but the directory
is specified by name to reduce clutter in the ouptut shown.

.. code-block:: bash

    $ pwd
    /home/roppenheimer/waves-eabm-tutorial
    $ tree build/tutorial_cubit
    build/tutorial_cubit/
    ├── amplitudes.inp
    ├── assembly.inp
    ├── boundary.inp
    ├── field_output.inp
    ├── history_output.inp
    ├── materials.inp
    ├── parts.inp
    ├── single_element_compression.abaqus_v6.env
    ├── single_element_compression.com
    ├── single_element_compression.dat
    ├── single_element_compression_DATACHECK.023
    ├── single_element_compression_DATACHECK.abaqus_v6.env
    ├── single_element_compression_DATACHECK.com
    ├── single_element_compression_DATACHECK.dat
    ├── single_element_compression_DATACHECK.mdl
    ├── single_element_compression_DATACHECK.msg
    ├── single_element_compression_DATACHECK.odb
    ├── single_element_compression_DATACHECK.prt
    ├── single_element_compression_DATACHECK.sim
    ├── single_element_compression_DATACHECK.stdout
    ├── single_element_compression_DATACHECK.stt
    ├── single_element_compression.inp
    ├── single_element_compression.msg
    ├── single_element_compression.odb
    ├── single_element_compression.prt
    ├── single_element_compression.sta
    ├── single_element_compression.stdout
    ├── single_element_geometry.cub
    ├── single_element_geometry.stdout
    ├── single_element_mesh.cub
    ├── single_element_mesh.inp
    ├── single_element_mesh.stdout
    ├── single_element_partition.cub
    └── single_element_partition.stdout

    0 directories, 34 files
