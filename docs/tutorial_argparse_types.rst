.. _tutorial_argparse_types:

############################
Tutorial: Input Verification
############################

The Abaqus journal files from :ref:`tutorial_geometry` and :ref:`tutorial_partition_mesh` already perform
some input verification by specifying the expected variable types. This input verification can be extended by user
specified type methods. This is useful when a journal file should limit the range of allowable float values, for
instance. In the case of these tutorials, one might wish to limit the width, height, and global seed parameters to
positive float values. The solution approach is sufficiently general to allow modsim owners to similarly implement
ranges of floats or integers, specific value choices, or any other restriction which may be necessary to ensure that a
simulation workflow is used within its designed assumptions.

**********
References
**********

* `Argparse type`_ :cite:`python`
* :ref:`tutorial_partition_mesh`
* :ref:`tutorial_parameter_substitution`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

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
        $ waves fetch --overwrite --tutorial 2 && mv tutorial_02_partition_mesh_SConstruct SConstruct
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'

4. Download and copy the ``tutorial_02_partition_mesh`` file to a new file named ``tutorial_argparse_types``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_02_partition_mesh && cp tutorial_02_partition_mesh tutorial_argparse_types
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

5. Create a new directory ``modsim_package/argparse_types``.

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials
   $ mkdir -p modsim_package/argparse_types

6. Copy the Abaqus journal files into the new directory ``modsim_package/argparse_types``

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials
   $ cp modsim_package/abaqus/rectangle_{geometry,partition,mesh}.py modsim_package/argparse_types

*************
Journal Files
*************

7. In the ``modsim_package`` directory, create a new file called ``argparse_types.py`` using the contents below

.. admonition:: waves-tutorials/modsim_package/argparse_types.py

    .. literalinclude:: modsim_package_argparse_types.py
        :language: Python
        :lineno-match:

The user-defined `Argparse type`_ function must take exactly one positional argument, which should correspond to the
string that will be parsed by the argparse interface. The function may perform any arbitrary verification checks and
return the type cast argument if all checks pass.

8. Make the following changes to the journal file imports and argparse option definitions.

.. admonition:: waves-tutorials/argparse_types/rectangle_geometry.py

   .. literalinclude:: argparse_types_rectangle_geometry.py
      :language: Python
      :diff: abaqus_rectangle_geometry.py

.. admonition:: waves-tutorials/argparse_types/rectangle_partition.py

   .. literalinclude:: argparse_types_rectangle_partition.py
      :language: Python
      :diff: abaqus_rectangle_partition.py

.. admonition:: waves-tutorials/argparse_types/rectangle_mesh.py

   .. literalinclude:: argparse_types_rectangle_mesh.py
      :language: Python
      :diff: abaqus_rectangle_mesh.py

Here we import the modsim package files as introduced in :ref:`tutorial_partition_mesh` for the meshing journal file,
but for all journal files to use the ``positive_float`` type check in the ``argparse`` interface.

**********
SConscript
**********

No change is required to the ``SConscript`` configuration file. The new journal file location will be changed in the
``SConstruct`` file below.

**********
SConstruct
**********

9. Add ``tutorial_argparse_types`` to the ``workflow_configurations`` list in the ``waves-tutorials/SConstruct``
   file.

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_partition_mesh` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_argparse_types_SConstruct
      :language: Python
      :diff: tutorials_tutorial_02_partition_mesh_SConstruct

In addition to the new target workflow ``tutorial_argparse_types``, the changes above point to the new
``argparse_types`` path containing the updated journal files.

*************
Build Targets
*************

10. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials
   $ scons tutorial_argparse_types
   scons: Reading SConscript files ...
   Checking whether abq2024 program exists.../apps/abaqus/Commands/abq2024
   Checking whether abq2021 program exists.../apps/abaqus/Commands/abq2021
   Checking whether abq2020 program exists.../apps/abaqus/Commands/abq2020
   scons: done reading SConscript files.
   scons: Building targets ...
   cd /home/roppenheimer/waves-tutorials/build/tutorial_argparse_types && /apps/abaqus/Commands/abaqus cae -noGui /home/roppenheimer/waves-tutorials/modsim_package/abaqus/rectangle_geometry.py -- > rectangle_geometry.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/build/tutorial_argparse_types && /apps/abaqus/Commands/abaqus cae -noGui /home/roppenheimer/waves-tutorials/modsim_package/abaqus/rectangle_partition.py -- > rectangle_partition.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/build/tutorial_argparse_types && /apps/abaqus/Commands/abaqus cae -noGui /home/roppenheimer/waves-tutorials/modsim_package/abaqus/rectangle_mesh.py -- > rectangle_mesh.stdout 2>&1
   scons: done building targets.

The build process, targets, and output files should be identical to that of :ref:`tutorial_partition_mesh`. You
can explore changes in behavior by modifying the ``subcommand_options`` of both ``tutorial_02_partition_mesh`` and
``tutorial_argparse_types`` to include negative floats and re-running both workflows. For instance, by adding the
following to the Geometry task definition.

.. code-block:: Python

   subcommand_options="--width '-1.0'"

See :ref:`tutorial_parameter_substitution` for more details about using the command-line interface and
``subcommand_options`` task argument.

************
Output Files
************

The contents of the new workflow should be identical to that of :ref:`tutorial_partition_mesh`.

.. code-block:: bash

    $ pwd
    /home/roppenheimer/waves-tutorials
    $ tree build/tutorial_02_partition_mesh/ build/tutorial_argparse_types/
    build/tutorial_02_partition_mesh/
    |-- abaqus.rpy
    |-- abaqus.rpy.1
    |-- abaqus.rpy.2
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
    build/tutorial_argparse_types/
    |-- abaqus.rpy
    |-- abaqus.rpy.1
    |-- abaqus.rpy.2
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

    0 directories, 26 files
