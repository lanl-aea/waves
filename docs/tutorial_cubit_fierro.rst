.. _tutorial_cubit_fierro:

######################
Tutorial: Cubit+Fierro
######################

.. include:: tutorial_cubit_alternate.txt

**********
References
**********

* `Cubit`_: Python Interface :cite:`cubit`
* `Cubit`_: Importing Cubit into Python :cite:`cubit`
* `Fierro`_ documentation :cite:`fierro,fierro-docs`
* `meshio`_ :cite:`meshio`
* `vtk`_ :cite:`vtk`
* `MPI`_ :cite:`mpi-forum`

***********
Environment
***********

.. warning::

   The Fierro tutorial requires a different compute environment than the other tutorials. The following commands create
   a dedicated environment for the use of this tutorial. You can also use your existing tutorial environment
   environment if you add the `FierroMechanics`_ channel and install the ``fierro-fe-cpu`` and ``meshio`` packages.

`SCons`_, `WAVES`_, and `Fierro`_ can be installed in a `Conda`_ environment with the `Conda`_ package manager. See the
`Conda installation`_ and `Conda environment management`_ documentation for more details about using `Conda`_.

1. Create the Fierro tutorials environment if it doesn't exist

   .. code-block::

      $ conda create --name waves-fierro-env --channel fierromechanics --channel conda-forge waves 'scons>=4.6' fierro-fe-cpu meshio

2. Activate the environment

   .. code-block::

      $ conda activate waves-fierro-env

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
The ``cubit`` and ``fierro`` files are relevant to the current tutorial. The ``abaqus`` and ``sierra`` workflows are
described in the complementary :ref:`tutorial_cubit_abaqus` and :ref:`tutorial_cubit_sierra`.

6. Review the ``cubit`` and ``fierro`` tutorials and compare them against the :ref:`tutorial_simulation` files.

The structure has changed enough that a diff view is not as useful. Instead the contents of the new SConscript files are
duplicated below.

.. admonition:: waves-tutorials/tutorial_cubit/cubit

   .. literalinclude:: tutorial_cubit_cubit
      :language: Python
      :lineno-match:

.. admonition:: waves-tutorials/tutorial_cubit/fierro

   .. literalinclude:: tutorial_cubit_fierro
      :language: Python
      :lineno-match:

*******************
Cubit Journal Files
*******************

Unlike :ref:`tutorial_cubit_abaqus` and :ref:`tutorial_cubit_sierra`, this tutorial creates a 3D cube geometry. The
`Fierro`_ implicit solver works best with 3D geometries and meshes. The 3D geometry, mesh, and simulation match the
uniaxial compression boundary conditions of the 2D simulation as closely as possible with the `Fierro`_ boundary
conditions.

7. Review the following journal files in the ``waves-tutorials/modsim_package/cubit`` directory.

The Cubit journal files include a similar CLI to the Abaqus journal files introduced in :ref:`tutorial_partition_mesh`
files. Besides the differences in Abaqus and Cubit commands, the major difference between the Abaqus and Cubit journal
files is the opportunity to use Python 3 with Cubit, where Abaqus journal files must use the Abaqus controlled
installation of Python 2. The API and CLI built from the Cubit journal files' docstrings may be found in the
:ref:`waves_tutorial_api` for :ref:`cubit_journal_api` and the :ref:`waves_tutorial_cli` for :ref:`cubit_journal_cli`,
respectively.

.. admonition:: waves-tutorials/tutorial_cubit/modsim_package/cubit/cube_geometry.py

   .. literalinclude:: cubit_cube_geometry.py
       :language: Python
       :lineno-match:

.. admonition:: waves-tutorials/tutorial_cubit/modsim_package/cubit/cube_partition.py

   .. literalinclude:: cubit_cube_partition.py
       :language: Python
       :lineno-match:

.. admonition:: waves-tutorials/tutorial_cubit/modsim_package/cubit/cube_mesh.py

   .. literalinclude:: cubit_cube_mesh.py
       :language: Python
       :lineno-match:

*************
Python Script
*************

Fierro doesn't read Sierra formatted (Genesis/Exodus) meshes natively. We need to convert from the Cubit Genesis mesh to
an older `vtk`_ ASCII text mesh file with `meshio`_. The `Fierro`_ development team provided a draft conversion script
that has been updated here to use a similar CLI to `meshio`_.

.. admonition:: waves-tutorials/tutorial_cubit/modsim_package/fierro/convert_to_vtk2ascii.py

   .. literalinclude:: fierro_convert_to_vtk2ascii.py
       :language: Python
       :lineno-match:

********************
Fierro Input File(s)
********************

8. Create or review the `Fierro`_ input file from the contents below

.. admonition:: waves-tutorials/tutorial_cubit_fierro/modsim_package/fierro/cube_compression.yaml

   .. literalinclude:: fierro_cube_compression.yaml
      :lineno-match:

**********
SConstruct
**********

Note that Fierro differs from other solvers in the tutorials. Fierro is deployed as a Conda package and is available in
the launching Conda environment. It is still good practice to check if the executable is available and provide helpful
feedback to developers about the excutable status and workflow configuration.

The structure has changed enough from the core tutorials that a diff view is not as useful. Instead the contents of the
SConstruct file is duplicated below.

.. admonition:: waves-tutorials/tutorial_cubit/SConstruct

   .. literalinclude:: tutorial_cubit_SConstruct
      :language: Python

*************
Build Targets
*************

9. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials/tutorial_cubit
   $ scons fierro
   scons: Reading SConscript files ...
   Checking whether /apps/abaqus/Commands/abq2024 program exists.../apps/abaqus/Commands/abq2024
   Checking whether abq2024 program exists...no
   Checking whether /apps/Cubit-16.12/cubit program exists.../apps/Cubit-16.12/cubit
   Checking whether cubit program exists...no
   Checking whether fierro-parallel-implicit program exists.../projects/aea_compute/waves-env/bin/fierro-parallel-implicit
   Sourcing the shell environment with command 'module use /projects/aea_compute/modulefiles && module load sierra' ...
   Checking whether sierra program exists.../projects/sierra/sierra5193/install/tools/sntools/engine/sierra
   scons: done reading SConscript files.
   scons: Building targets ...
   Copy("build/fierro/cube_compression.yaml", "modsim_package/fierro/cube_compression.yaml")
   Copy("build/fierro/elasticity3D.xml", "modsim_package/fierro/elasticity3D.xml")
   cd /home/roppenheimer/waves-tutorials/tutorial_cubit/build/fierro && python
   /home/roppenheimer/waves-tutorials/tutorial_cubit/modsim_package/cubit/cube_geometry.py >
   /home/roppenheimer/waves-tutorials/tutorial_cubit/build/fierro/cube_geometry.cub.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_cubit/build/fierro && python
   /home/roppenheimer/waves-tutorials/tutorial_cubit/modsim_package/cubit/cube_partition.py >
   /home/roppenheimer/waves-tutorials/tutorial_cubit/build/fierro/cube_partition.cub.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_cubit/build/fierro && python
   /home/roppenheimer/waves-tutorials/tutorial_cubit/modsim_package/cubit/cube_mesh.py --element-type HEX
   --solver sierra > /home/roppenheimer/waves-tutorials/tutorial_cubit/build/fierro/cube_mesh.g.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_cubit/build/fierro && python
   /home/roppenheimer/waves-tutorials/tutorial_cubit/modsim_package/fierro/convert_to_vtk2ascii.py
   --input-format=exodus /home/roppenheimer/waves-tutorials/tutorial_cubit/build/fierro/cube_mesh.g
   /home/roppenheimer/waves-tutorials/tutorial_cubit/build/fierro/cube_mesh.vtk >
   /home/roppenheimer/waves-tutorials/tutorial_cubit/build/fierro/cube_mesh.vtk.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_cubit/build/fierro && mpirun -np 1
   fierro-parallel-implicit
   /home/roppenheimer/waves-tutorials/tutorial_cubit/build/fierro/cube_compression.yaml >
   /home/roppenheimer/waves-tutorials/tutorial_cubit/build/fierro/cube_compression.stdout 2>&1
   scons: done building targets.

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_cubit
   $ tree build/fierro/
   build/fierro/
   |-- TecplotTO0.dat
   |-- TecplotTO_undeformed0.dat
   |-- cube_compression.stdout
   |-- cube_compression.yaml
   |-- cube_geometry.cub
   |-- cube_geometry.cub.stdout
   |-- cube_mesh.cub
   |-- cube_mesh.g
   |-- cube_mesh.g.stdout
   |-- cube_mesh.vtk
   |-- cube_mesh.vtk.stdout
   |-- cube_partition.cub
   |-- cube_partition.cub.stdout
   `-- elasticity3D.xml

   0 directories, 14 files
