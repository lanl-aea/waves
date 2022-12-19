.. _tutorial_argparse_types_waves:

############################
Tutorial: Input Verification
############################

The Abaqus journal files from :ref:`tutorial_geometry_waves` and :ref:`tutorial_partition_mesh_waves` already perform
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
* :ref:`tutorial_partition_mesh_waves`
* :ref:`tutorial_parameter_substitution_waves`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Copy the ``tutorial_02_partition_mesh`` file to a new file named ``tutorial_argparse_types``

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_02_partition_mesh tutorial_argparse_types

4. Create a new directory ``eabm_package/argparse_types``.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir -p eabm_package/argparse_types

5. Copy the Abaqus journal files into the new directory ``eabm_package/argparse_types``

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp eabm_package/abaqus/single_element_{geometry,partition,mesh}.py eabm_package/argparse_types

*************
Journal Files
*************

6. In the ``eabm_package`` directory, create a new file called ``argparse_types.py`` using the contents below

.. admonition:: waves-eabm-tutorial/eabm_package/argparse_types.py

    .. literalinclude:: eabm_package_argparse_types.py
        :language: Python
        :lineno-match:

The user-defined `Argparse type`_ function must take exactly one positional argument, which should correspond to the
string that will be parsed by the argparse interface. The function may perform any arbitrary verification checks and
return the type cast argument if all checks pass.

7. Make the following changes to the journal file imports and argparse option definitions.

.. admonition:: waves-eabm-tutorial/argparse_types/single_element_geometry.py

   .. literalinclude:: argparse_types_single_element_geometry.py
      :language: Python
      :diff: abaqus_single_element_geometry.py

.. admonition:: waves-eabm-tutorial/argparse_types/single_element_partition.py

   .. literalinclude:: argparse_types_single_element_partition.py
      :language: Python
      :diff: abaqus_single_element_partition.py

.. admonition:: waves-eabm-tutorial/argparse_types/single_element_mesh.py

   .. literalinclude:: argparse_types_single_element_mesh.py
      :language: Python
      :diff: abaqus_single_element_mesh.py

Here we import the eabm package files as introduced in :ref:`tutorial_partition_mesh_waves` for the meshing journal
file, but for all journal files to use the ``positive_float`` type check in the ``argparse`` interface.

**********
SConscript
**********

No change is required to the ``SConscript`` configuration file. The new journal file location will be changed in the
``SConstruct`` file below.

**********
SConstruct
**********

7. Add ``tutorial_argparse_types`` to the ``workflow_configurations`` list in the ``waves-eabm-tutorial/SConstruct``
   file.

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_partition_mesh_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: tutorials_tutorial_argparse_types_SConstruct
      :language: Python
      :diff: tutorials_tutorial_02_partition_mesh_SConstruct

In addition to the new target workflow ``tutorial_argparse_types``, the changes above point to the new
``argparse_types`` path containing the updated journal files.

*************
Build Targets
*************

8. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_argparse_types
   scons: Reading SConscript files ...
   Checking whether abq2022 program exists.../apps/abaqus/Commands/abq2022
   Checking whether abq2021 program exists.../apps/abaqus/Commands/abq2021
   Checking whether abq2020 program exists.../apps/abaqus/Commands/abq2020
   scons: done reading SConscript files.
   scons: Building targets ...
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_argparse_types && /apps/abaqus/Commands/abaqus -information environment
   > single_element_geometry.abaqus_v6.env
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_argparse_types && /apps/abaqus/Commands/abaqus cae -noGui
   /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_geometry.py -- > single_element_geometry.stdout 2>&1
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_argparse_types && /apps/abaqus/Commands/abaqus -information environment
   > single_element_partition.abaqus_v6.env
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_argparse_types && /apps/abaqus/Commands/abaqus cae -noGui
   /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_partition.py -- > single_element_partition.stdout 2>&1
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_argparse_types && /apps/abaqus/Commands/abaqus -information environment
   > single_element_mesh.abaqus_v6.env
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_argparse_types && /apps/abaqus/Commands/abaqus cae -noGui
   /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_mesh.py -- > single_element_mesh.stdout 2>&1
   scons: done building targets.

The build process, targets, and output files should be identical to that of :ref:`tutorial_partition_mesh_waves`. You
can explore changes in behavior by modifying the ``journal_options`` of both ``tutorial_02_partition_mesh`` and
``tutorial_argparse_types`` to include negative floats and re-running both workflows. For instance, by adding the
following to the Geometry task definition.

.. code-block:: Python

   journal_options="--width '-1.0'"

See :ref:`tutorial_parameter_substitution_waves` for more details about using the command line interface and
``journal_options`` task argument.

************
Output Files
************

The contents of the new workflow should be identical to that of :ref:`tutorial_partition_mesh_waves`.

.. code-block:: bash

    $ pwd
    /home/roppenheimer/waves-eabm-tutorial
    $ tree build/tutorial_02_partition_mesh/ build/tutorial_argparse_types/
    build/tutorial_02_partition_mesh/
    |-- abaqus.rpy
    |-- abaqus.rpy.1
    |-- abaqus.rpy.2
    |-- single_element_geometry.abaqus_v6.env
    |-- single_element_geometry.cae
    |-- single_element_geometry.jnl
    |-- single_element_geometry.stdout
    |-- single_element_mesh.abaqus_v6.env
    |-- single_element_mesh.cae
    |-- single_element_mesh.inp
    |-- single_element_mesh.jnl
    |-- single_element_mesh.stdout
    |-- single_element_partition.abaqus_v6.env
    |-- single_element_partition.cae
    |-- single_element_partition.jnl
    `-- single_element_partition.stdout
    build/tutorial_argparse_types/
    |-- abaqus.rpy
    |-- abaqus.rpy.1
    |-- abaqus.rpy.2
    |-- single_element_geometry.abaqus_v6.env
    |-- single_element_geometry.cae
    |-- single_element_geometry.jnl
    |-- single_element_geometry.stdout
    |-- single_element_mesh.abaqus_v6.env
    |-- single_element_mesh.cae
    |-- single_element_mesh.inp
    |-- single_element_mesh.jnl
    |-- single_element_mesh.stdout
    |-- single_element_partition.abaqus_v6.env
    |-- single_element_partition.cae
    |-- single_element_partition.jnl
    `-- single_element_partition.stdout

    0 directories, 32 files
