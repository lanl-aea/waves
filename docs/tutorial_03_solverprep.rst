.. _tutorial_solverprep:

#######################
Tutorial 03: SolverPrep
#######################

**********
References
**********

* Bash concepts used in this tutorial: `Bash Variables`_, `Bash Arrays`_, `Bash Parameter Expansion`_ :cite:`gnu-bash`
* `Abaqus *INCLUDE`_ keyword documentation :cite:`ABAQUS`
* `SCons Pseudo-Builder`_ and `SCons Copy`_ :cite:`scons-user`

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
        $ waves fetch --overwrite --tutorial 2 && mv tutorial_02_partition_mesh_SConstruct SConstruct
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'

4. Fetch the ``tutorial_02_partition_mesh`` file and create a new file named ``tutorial_03_solverprep``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_02_partition_mesh && cp tutorial_02_partition_mesh tutorial_03_solverprep
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

******************
Solver Input Files
******************

5. Fetch the `WAVES tutorials abaqus source files`_ into your existing ``modsim_package/abaqus`` sub-directory
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch 'tutorials/modsim_package/abaqus/*.inp' --destination modsim_package/abaqus
   WAVES fetch
   Destination directory: 'modsim_package/abaqus'

This action will fetch the source files we included in the
``tutorial_03_solverprep`` file into the ``waves-tutorials/modsim_package/abaqus/``
directory. Check the contents of this directory using the ``ls`` command.

.. code-block::

    $ pwd
    /home/roppenheimer/waves-tutorials
    $ ls modsim_package/abaqus
    abaqus_utilities.py  history_output.inp  rectangle_compression.inp
    assembly.inp         __init__.py         rectangle_geometry.py
    boundary.inp         materials.inp       rectangle_mesh.py
    field_output.inp     parts.inp           rectangle_partition.py

.. _tutorials_tutorial_solverprep:

**********
SConscript
**********

.. note::

    There is a large section of lines in the ``SConscript`` file that are not included
    before the next section of code shown here, as they are identical to those from
    :ref:`tutorial_partition_mesh`. The ``diff`` of the ``SConscript`` file at the
    end of the :ref:`tutorials_tutorial_solverprep` section will demonstrate this
    more clearly.

6. Modify your ``tutorial_03_solverprep`` file by adding the contents shown below immediately after the code
   pertaining to ``# Mesh`` from the previous tutorial, and above the ``# Collector alias`` code.

.. admonition:: waves-tutorials/tutorial_03_solverprep

    .. literalinclude:: tutorials_tutorial_03_solverprep
       :language: Python
       :lineno-match:
       :start-after: marker-3
       :end-before: marker-4

The ``abaqus_source_list`` contains the names of all the files that are used to build the Abaqus model. The
``{model}_compression.inp`` file is the primary input file, and the other files in the ``abaqus_source_list`` are
included within it. See the `Abaqus *INCLUDE`_ keyword documentaiton :cite:`ABAQUS` for more information about how
this is implemented.

Each file in the ``abaqus_source_list`` is specified with its absolute path with the SCons ``#`` project root feature
which is replaced by the parent directory of the ``SConstruct`` file. After constructing the ``abaqus_source_list``, we
must first convert each string (which represent the absolute paths of each file in the list) to a `Python pathlib`_
object. While not strictly neccessary for the :meth:`waves.scons_extensions.copy_substfile` pseudo-builder, the `Python
pathlib`_ objects are used elsewhere in the ``SConscript`` file.

Just as in the previous tutorials, we now need to extend the ``workflow`` list. Recall that we have already extended the
workflow three times - once each for the Geometry, Partition, and Mesh processes.

Unlike the ``AbaqusJournal`` builder, the :meth:`waves.scons_extensions.copy_substfile` is not a builder, but an `SCons
Pseudo-Builder`_ which only requires the source file name(s). This is possible because the target file can be inferred
from the copy operation and build directory. With this pseudo-builder interface, it's also possible to pass a list of
source files instead of defining a unique task for each item in the ``abaqus_source_list``. The
:meth:`waves.scons_extensions.copy_substfile` pseudo-builder will construct the per-file tasks automatically and return
the complete list of targets.

In summary of the changes you just made to the ``tutorial_03_solverprep`` file, a ``diff`` against the ``SConscript``
file from :ref:`tutorial_partition_mesh` is included below to help identify the changes made in this tutorial.

.. admonition:: waves-tutorials/tutorial_03_solverprep

   .. literalinclude:: tutorials_tutorial_03_solverprep
      :language: Python
      :diff: tutorials_tutorial_02_partition_mesh

**********
SConstruct
**********

7. Add ``tutorial_03_solverprep`` to the ``workflow_configurations`` list in the ``SConstruct`` file.

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_partition_mesh` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_03_solverprep_SConstruct
      :language: Python
      :diff: tutorials_tutorial_02_partition_mesh_SConstruct


*************
Build Targets
*************

8. Build the new targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons tutorial_03_solverprep
   scons: Reading SConscript files ...
   Checking whether /apps/abaqus/Commands/abq2024 program exists.../apps/abaqus/Commands/abq2024
   Checking whether abq2024 program exists.../apps/abaqus/Commands/abq2024
   scons: done reading SConscript files.
   scons: Building targets ...
   cd /home/roppenheimer/waves-tutorials/build/tutorial_03_solverprep && /apps/abaqus/Commands/abq2024 cae -noGui /home/roppenheimer/waves-tutorials/modsim_package/abaqus/rectangle_geometry.py -- > rectangle_geometry.cae.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/build/tutorial_03_solverprep && /apps/abaqus/Commands/abq2024 cae -noGui /home/roppenheimer/waves-tutorials/modsim_package/abaqus/rectangle_partition.py -- > rectangle_partition.cae.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/build/tutorial_03_solverprep && /apps/abaqus/Commands/abq2024 cae -noGui /home/roppenheimer/waves-tutorials/modsim_package/abaqus/rectangle_mesh.py -- > rectangle_mesh.inp.stdout 2>&1
   Copy("build/tutorial_03_solverprep/rectangle_compression.inp", "modsim_package/abaqus/rectangle_compression.inp")
   Copy("build/tutorial_03_solverprep/assembly.inp", "modsim_package/abaqus/assembly.inp")
   Copy("build/tutorial_03_solverprep/boundary.inp", "modsim_package/abaqus/boundary.inp")
   Copy("build/tutorial_03_solverprep/field_output.inp", "modsim_package/abaqus/field_output.inp")
   Copy("build/tutorial_03_solverprep/materials.inp", "modsim_package/abaqus/materials.inp")
   Copy("build/tutorial_03_solverprep/parts.inp", "modsim_package/abaqus/parts.inp")
   Copy("build/tutorial_03_solverprep/history_output.inp", "modsim_package/abaqus/history_output.inp")
   scons: done building targets.

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the
``build`` directory, as shown below.

.. code-block:: bash

    $ pwd
    /home/roppenheimer/waves-tutorials
    $ tree build/tutorial_01_geometry/ build/tutorial_02_partition_mesh/ build/tutorial_03_solverprep/
    build/tutorial_01_geometry/
    |-- abaqus.rpy
    |-- rectangle_geometry.cae
    |-- rectangle_geometry.cae.stdout
    `-- rectangle_geometry.jnl
    build/tutorial_02_partition_mesh/
    |-- abaqus.rpy
    |-- abaqus.rpy.1
    |-- abaqus.rpy.2
    |-- rectangle_geometry.cae
    |-- rectangle_geometry.cae.stdout
    |-- rectangle_geometry.jnl
    |-- rectangle_mesh.cae
    |-- rectangle_mesh.inp
    |-- rectangle_mesh.inp.stdout
    |-- rectangle_mesh.jnl
    |-- rectangle_partition.cae
    |-- rectangle_partition.cae.stdout
    `-- rectangle_partition.jnl
    build/tutorial_03_solverprep/
    |-- abaqus.rpy
    |-- abaqus.rpy.1
    |-- abaqus.rpy.2
    |-- assembly.inp
    |-- boundary.inp
    |-- field_output.inp
    |-- history_output.inp
    |-- materials.inp
    |-- parts.inp
    |-- rectangle_compression.inp
    |-- rectangle_geometry.cae
    |-- rectangle_geometry.cae.stdout
    |-- rectangle_geometry.jnl
    |-- rectangle_mesh.cae
    |-- rectangle_mesh.inp
    |-- rectangle_mesh.inp.stdout
    |-- rectangle_mesh.jnl
    |-- rectangle_partition.cae
    |-- rectangle_partition.cae.stdout
    `-- rectangle_partition.jnl

    0 directories, 36 files

Inside the build directory are three sub-directories. ``tutorial_01_geometry`` and
``tutorial_02_partition_mesh``  remain from the previous two tutorials. The third
directory, ``tutorial_03_solverprep``, pertains to the targets we just built.

It is worth noting that the ``tutorial_03_solverprep`` build directory contains all the
files from the previous two tutorials. The additional files are the files from the
``abaqus_source_list`` that were acted on with the :meth:`waves.scons_extensions.copy_substfile`
pseudo-builder. In this case, the files were simply copied into the build directory with no
modification to the source code. :ref:`tutorial_parameter_substitution` will discuss
how parameters can be inserted into these solver input files.

**********************
Workflow Visualization
**********************

View the workflow directed graph by running the following command and opening the image in your preferred image viewer.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves visualize tutorial_03_solverprep --output-file tutorial_03_solverprep.png --width=28 --height=5 --exclude-list /usr/bin .stdout .jnl

The output should look similar to the figure below.

.. raw:: latex

    \begin{landscape}
        \vspace*{\fill}

.. figure:: tutorial_03_solverprep.png
   :align: center
   :width: 100%

.. raw:: latex

        \vspace*{\fill}
    \end{landscape}

Compared to :ref:`tutorial_partition_mesh`, the workflow has grown significantly. Of course, if you were managing
this workflow manually, the source ``*.inp`` files would probably be managed as a single file. Here, the files are split
in anticipation of larger modsim projects where a simulation may be recombined with many variations of materials, parts,
boundary conditions, or loading steps. The piecewise nature of the input file minimizes data duplication over simulation
combinations.

For the tutorials, the piecewise input files also fill in as a surrogate to demonstrate the large number of files found
in modsim projects of moderate to large complexity and in modsim projects with large parameter studies. In practice, the
modsim owner should balance priorities of code duplication and repository file count for the needs of the projects and
organization. While it's tempting to reduce duplication to a minimum, there may be good reasons to provide clean
separation between simulation input definitions. There is also an on-boarding cost found with many separate,
re-usable files and the associated high file count. Regardless, the modsim repository directory structure and design
choices should be documented in a developer manual with regular updates to match the existing implementation.
