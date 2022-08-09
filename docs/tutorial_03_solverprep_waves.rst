.. _tutorial_solverprep_waves:

#######################
Tutorial 03: SolverPrep
#######################

**********
References
**********

* Bash concepts used in this tutorial: `Bash Variables`_, `Bash Arrays`_, `Bash Parameter Expansion`_ :cite:`gnu-bash`
* `Abaqus *INCLUDE`_ keyword documentation :cite:`ABAQUS`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Create a directory ``tutorial_03_solverprep`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir tutorial_03_solverprep

4. Copy the ``tutorial_02_partition_mesh/SConscript`` file into the newly created ``tutorial_03_solverprep``
   directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_02_partition_mesh/SConscript tutorial_03_solverprep/

******************
Solver Input Files
******************

5. Download and copy the `WAVES-EABM abaqus source files`_ into your existing
   ``eabm_package/abaqus`` sub-directory. If you're on a linux system with `git`_ installed and
   read access on the `WAVES`_ repository, you can use `git archive`_ as below.

.. note::

    The commands in the code block below are intended for the user to copy and paste into
    their bash shell. These commands utilize the concepts of `Bash Variables`_, `Bash
    Arrays`_ and `Bash Parameter Expansion`_.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-eabm-tutorial

   $ file_list=("single_element_compression" "amplitudes" "assembly" "boundary" "field_output" "materials" "parts" "history_output")
   $ file_list=("${file_list[@]/%/.inp}")
   $ repo_ssh="ssh://git@re-git.lanl.gov:10022/aea/python-projects/waves.git"
   $ git archive --format=zip --remote=$repo_ssh HEAD:eabm/eabm_package/abaqus ${file_list[*]} > source_abaqus.zip
   $ unzip source_abaqus.zip -d eabm_package/abaqus

This action will unzip the source files we included in the
``tutorial_03_solverprep/SConscript`` file into the ``waves-eabm-tutorial/eabm_package/abaqus/``
directory. Check the contents of this directory using the ``ls`` command.

.. code-block::

    $ pwd
    /home/roppenheimer/waves-eabm-tutorial
    $ ls eabm_package/abaqus
    abaqus_journal_utilities.py  materials.inp
    amplitudes.inp               parts.inp
    assembly.inp                 single_element_compression.inp
    boundary.inp                 single_element_geometry.py
    field_output.inp             single_element_mesh.py
    history_output.inp           single_element_partition.py

.. _tutorial_solverprep_waves_SConscript:

**********
SConscript
**********

6. Add the highlighted import statement shown below to the
   ``tutorial_03_solverprep/SConscript`` file.

.. admonition:: waves-eabm-tutorial/tutorial_03_solverprep/SConscript

    .. literalinclude:: tutorial_03_solverprep_SConscript
       :language: Python
       :lineno-match:
       :emphasize-lines: 5
       :end-before: marker-1

The first few lines of the ``SConscript`` file should look very familiar with exception to
the single highlighted line. In this tutorial, we need to import the ``waves`` module, as
we will require a custom builder that functions differently than the previously used
:meth:`waves.builders.abaqus_journal` builder.

.. note::

    There is a large section of lines in the ``SConscript`` file that are not included
    before the next section of code shown here, as they are identical to those from
    :ref:`tutorial_partition_mesh_waves`. The ``diff`` of the ``SConscript`` file at the
    end of the :ref:`tutorial_solverprep_waves_SConscript` section will demonstrate this
    more clearly.

7. Modify your ``tutorial_03_solverprep/SConscript`` file by adding the contents shown
   below immediately after the code pertaining to ``# Mesh`` from the previous tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_03_solverprep/SConscript

    .. literalinclude:: tutorial_03_solverprep_SConscript
       :language: Python
       :lineno-match:
       :start-after: marker-3
       :end-before: marker-4

The ``abaqus_source_list`` contains the names of all the files that are used to build the Abaqus model. The
``{model}_compression.inp`` file is the primary input file, and the other files in the ``abaqus_source_list`` are
included within it. See the `Abaqus *INCLUDE`_ keyword documentaiton :cite:`ABAQUS` for more information about how
this is implemented.

Each file in the ``abaqus_source_list`` is specified with its absolute path. `SCons`_
interprets the ``#`` character in any target or source string as the absolute path to the
project root directory. The ``abaqus_source_dir`` variable was previously constructed
using variables from the ``env`` object. After constructing the ``abaqus_source_list``, we
must first convert each string (which represent the aboslute paths of each file in the
list) to a `Python pathlib`_ object. While not strictly neccessary for the
:meth:`waves.builders.copy_substitute` method, the `Python pathlib`_ objects are used
elsewhere in the `SConscript` file.

Just as in the previous tutorials, we now need to extend the ``workflow`` list. Recall
that we have already extended the workflow three times - once each for the Geometry,
Partition, and Mesh processes. Note that the syntax in this case is different from before,
as we now need to call the :meth:`waves.builders.copy_substitute` builder as a function
from the ``waves`` module. This is required because we need to perform the
``copy_substitute`` task for each item in the ``abaqus_source_list``.

In summary of the changes you just made to the ``tutorial_03_solverprep/SConscript`` file,
a ``diff`` against the ``SConscript`` file from :ref:`tutorial_partition_mesh_waves` is
included below to help identify the changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_03_solverprep/SConscript

   .. literalinclude:: tutorial_03_solverprep_SConscript
      :language: Python
      :diff: tutorial_02_partition_mesh_SConscript

**********
SConstruct
**********

8. Add ``tutorial_03_solverprep`` to the ``eabm_simulation_directories`` list in the
   ``waves-eabm-tutorial/SConstruct`` file.

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_partition_mesh_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: eabm_tutorial_03_solverprep_SConstruct
      :language: Python
      :diff: eabm_tutorial_02_partition_mesh_SConstruct

*************
Build Targets
*************

5. Build the new targets

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_03_solverprep
   scons: Reading SConscript files ...
   Checking whether abq2021 program exists.../apps/abaqus/Commands/abq2021
   Checking whether abq2020 program exists.../apps/abaqus/Commands/abq2020
   scons: done reading SConscript files.
   scons: Building targets ...
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_03_solverprep && /apps/abaqus/Commands/abaqus -information environment
   > single_element_geometry.abaqus_v6.env
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_03_solverprep && /apps/abaqus/Commands/abaqus cae -noGui
   /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_geometry.py -- > single_element_geometry.stdout 2>&1
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_03_solverprep && /apps/abaqus/Commands/abaqus -information environment
   > single_element_partition.abaqus_v6.env
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_03_solverprep && /apps/abaqus/Commands/abaqus cae -noGui
   /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_partition.py -- > single_element_partition.stdout 2>&1
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_03_solverprep && /apps/abaqus/Commands/abaqus -information environment
   > single_element_mesh.abaqus_v6.env
   cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_03_solverprep && /apps/abaqus/Commands/abaqus cae -noGui
   /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_mesh.py -- > single_element_mesh.stdout 2>&1
   Copy("build/tutorial_03_solverprep/single_element_compression.inp",
   "eabm_package/abaqus/single_element_compression.inp")
   Copy("build/tutorial_03_solverprep/amplitudes.inp", "eabm_package/abaqus/amplitudes.inp")
   Copy("build/tutorial_03_solverprep/assembly.inp", "eabm_package/abaqus/assembly.inp")
   Copy("build/tutorial_03_solverprep/boundary.inp", "eabm_package/abaqus/boundary.inp")
   Copy("build/tutorial_03_solverprep/field_output.inp", "eabm_package/abaqus/field_output.inp")
   Copy("build/tutorial_03_solverprep/materials.inp", "eabm_package/abaqus/materials.inp")
   Copy("build/tutorial_03_solverprep/parts.inp", "eabm_package/abaqus/parts.inp")
   Copy("build/tutorial_03_solverprep/history_output.inp", "eabm_package/abaqus/history_output.inp")
   scons: done building targets.

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the
``build`` directory, as shown below.

.. code-block:: bash

    $ pwd
    /home/roppenheimer/waves-eabm-tutorial
    $ tree build/
    ├── tutorial_01_geometry
    │   ├── abaqus.rpy
    │   ├── single_element_geometry.abaqus_v6.env
    │   ├── single_element_geometry.cae
    │   ├── single_element_geometry.jnl
    │   └── single_element_geometry.stdout
    ├── tutorial_02_partition_mesh
    │   ├── abaqus.rpy
    │   ├── abaqus.rpy.1
    │   ├── abaqus.rpy.2
    │   ├── single_element_geometry.abaqus_v6.env
    │   ├── single_element_geometry.cae
    │   ├── single_element_geometry.jnl
    │   ├── single_element_geometry.stdout
    │   ├── single_element_mesh.abaqus_v6.env
    │   ├── single_element_mesh.cae
    │   ├── single_element_mesh.inp
    │   ├── single_element_mesh.jnl
    │   ├── single_element_mesh.stdout
    │   ├── single_element_partition.abaqus_v6.env
    │   ├── single_element_partition.cae
    │   ├── single_element_partition.jnl
    │   └── single_element_partition.stdout
    └── tutorial_03_solverprep
        ├── abaqus.rpy
        ├── abaqus.rpy.1
        ├── abaqus.rpy.2
        ├── amplitudes.inp
        ├── assembly.inp
        ├── boundary.inp
        ├── field_output.inp
        ├── history_output.inp
        ├── materials.inp
        ├── parts.inp
        ├── single_element_compression.inp
        ├── single_element_geometry.abaqus_v6.env
        ├── single_element_geometry.cae
        ├── single_element_geometry.jnl
        ├── single_element_geometry.stdout
        ├── single_element_mesh.abaqus_v6.env
        ├── single_element_mesh.cae
        ├── single_element_mesh.inp
        ├── single_element_mesh.jnl
        ├── single_element_mesh.stdout
        ├── single_element_partition.abaqus_v6.env
        ├── single_element_partition.cae
        ├── single_element_partition.jnl
        └── single_element_partition.stdout

    3 directories, 45 files

Inside the build directory are three sub-directories. ``tutorial_01_geometry`` and
``tutorial_02_partition_mesh``  remain from the previous two tutorials. The third
directory, ``tutorial_03_solverprep``, pertains to the targets we just built.

It is worth noting that the ``tutorial_03_solverprep`` build directory contains all the
files from the previous two tutorials. The additional files are the files from the
``abaqus_source_list`` that were acted on with the :meth:`waves.builders.copy_substitute`
builder. In this case, the files were simply copied into the build directory with no
modification to the source code. :ref:`tutorial_parameter_substitution_waves` will discuss
how parameters can be inserted into these solver input files.
