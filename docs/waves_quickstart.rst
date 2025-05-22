.. _waves_quickstart:

##################
Quickstart: Abaqus
##################

This tutorial is also available with a fully open-source, conda-forge based compute environment using the `Gmsh`_ mesher
and `CalculiX`_ FEA solver in :ref:`tutorial_gmsh_calculix`.

.. include:: tutorial_quickstart_introduction.txt

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

.. include:: version_check_warning.txt

*******************
Directory Structure
*******************

3. Create the project directory structure and copy the `WAVES quickstart source files`_ into the ``~/waves-tutorials/waves_quickstart``
   sub-directory with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

      $ waves fetch tutorials/waves_quickstart --destination ~/waves-tutorials/waves_quickstart
      WAVES fetch
      Destination directory: '/home/roppenheimer/waves-tutorials/waves_quickstart'
      $ cd ~/waves-tutorials/waves_quickstart
      $ pwd
      /home/roppenheimer/waves-tutorials/waves_quickstart

**********
SConscript
**********

.. include:: tutorial_quickstart_sconscript.txt

.. admonition:: waves_quickstart/SConscript

    .. literalinclude:: waves_quickstart_SConscript
       :language: Python
       :lineno-match:

**********
SConstruct
**********

.. include:: tutorial_quickstart_sconstruct_1.txt

.. admonition:: waves_quickstart/SConstruct

    .. literalinclude:: waves_quickstart_SConstruct
       :language: Python
       :lineno-match:
       :start-at: # Define parameter studies
       :end-before: # Add workflow(s)

.. include:: tutorial_quickstart_sconstruct_2.txt

.. admonition:: waves_quickstart/SConstruct

    .. literalinclude:: waves_quickstart_SConstruct
       :language: Python
       :lineno-match:
       :start-at: # Add workflow(s)
       :end-before: # List all aliases in help message

.. include:: tutorial_quickstart_sconstruct_3.txt

****************
Building targets
****************

.. note::

   You may need to pass the relative or absolute path to your Abaqus installation when running the workflow.

   .. code-block::

      scons --abaqus-command /path/to/executable/abaqus ...

   You can also edit the SConstruct file contents below to include your Abaqus installation in the default search for an
   Abaqus executable.

   .. admonition:: waves_quickstart/SConstruct

       .. literalinclude:: waves_quickstart_SConstruct
          :language: Python
          :lineno-match:
          :start-after: documentation-marker-default-abaqus-commands-start
          :end-before: documentation-marker-default-abaqus-commands-end

   The :meth:`waves.scons_extensions.WAVESEnvironment.AddProgram` method performs an ordered preference search for
   executables by absolute and relative paths in the system ``PATH``.

.. include:: tutorial_quickstart_build_1.txt

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/waves_quickstart
   $ scons nominal
   scons: Reading SConscript files ...
   Checking whether '/apps/abaqus/Commands/abq2024' program exists.../apps/abaqus/Commands/abq2024
   Checking whether '/usr/projects/ea/abaqus/Commands/abq2024' program exists...no
   Checking whether 'abq2024' program exists...no
   Checking whether 'abaqus' program exists...no
   scons: done reading SConscript files.
   scons: Building targets ...
   Copy("build/nominal/rectangle_compression.inp.in", "rectangle_compression.inp.in")
   Creating 'build/nominal/rectangle_compression.inp'
   cd /home/roppenheimer/waves-tutorials/waves_quickstart/build/nominal && /apps/abaqus/Commands/abq2024 cae -noGUI /home/roppenheimer/waves-tutorials/waves_quickstart/build/nominal/rectangle_geometry.py -- --width 1.0 --height 1.0 > /home/roppenheimer/waves-tutorials/waves_quickstart/build/nominal/rectangle_geometry.cae.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/waves_quickstart/build/nominal && /apps/abaqus/Commands/abq2024 cae -noGUI /home/roppenheimer/waves-tutorials/waves_quickstart/build/nominal/rectangle_partition.py -- --width 1.0 --height 1.0 > /home/roppenheimer/waves-tutorials/waves_quickstart/build/nominal/rectangle_partition.cae.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/waves_quickstart/build/nominal && /apps/abaqus/Commands/abq2024 cae -noGUI /home/roppenheimer/waves-tutorials/waves_quickstart/build/nominal/rectangle_mesh.py -- --global-seed 1.0 > /home/roppenheimer/waves-tutorials/waves_quickstart/build/nominal/rectangle_mesh.inp.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/waves_quickstart/build/nominal && /apps/abaqus/Commands/abq2024 -interactive -ask_delete no -job rectangle_compression -input rectangle_compression -double both > /home/roppenheimer/waves-tutorials/waves_quickstart/build/nominal/rectangle_compression.stdout 2>&1
   _build_odb_extract(["build/nominal/rectangle_compression.h5", "build/nominal/rectangle_compression_datasets.h5", "build/nominal/rectangle_compression.csv"], ["build/nominal/rectangle_compression.odb"])
   cd /home/roppenheimer/waves-tutorials/waves_quickstart/build/nominal && python /home/roppenheimer/waves-tutorials/waves_quickstart/build/nominal/post_processing.py --input-file /home/roppenheimer/waves-tutorials/waves_quickstart/build/nominal/rectangle_compression_datasets.h5 --output-file stress_strain.pdf --x-units mm/mm --y-units MPa > /home/roppenheimer/waves-tutorials/waves_quickstart/build/nominal/stress_strain.pdf.stdout 2>&1
   scons: done building targets.

.. include:: tutorial_quickstart_build_2.txt

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/waves_quickstart
   $ ls build/nominal/stress_strain.pdf
   build/nominal/stress_strain.pdf

.. figure:: waves_quickstart_stress_strain.png
   :align: center
   :width: 50%

.. include:: tutorial_quickstart_build_3.txt

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/waves_quickstart
   $ rm build/nominal/rectangle_mesh.inp
   $ scons nominal
   scons: Reading SConscript files ...
   Checking whether '/apps/abaqus/Commands/abq2024' program exists.../apps/abaqus/Commands/abq2024
   Checking whether '/usr/projects/ea/abaqus/Commands/abq2024' program exists...no
   Checking whether 'abq2024' program exists...no
   Checking whether 'abaqus' program exists...no
   scons: done reading SConscript files.
   scons: Building targets ...
   cd /home/roppenheimer/waves-tutorials/waves_quickstart/build/nominal && /apps/abaqus/Commands/abq2024 cae -noGUI /home/roppenheimer/waves-tutorials/waves_quickstart/build/nominal/rectangle_mesh.py -- --global-seed 1.0 > /home/roppenheimer/waves-tutorials/waves_quickstart/build/nominal/rectangle_mesh.inp.stdout 2>&1
   scons: `nominal' is up to date.
   scons: done building targets.

.. include:: tutorial_quickstart_build_4.txt

************
Output Files
************

An example of the full nominal workflow output files is found below using the ``tree`` command. If ``tree`` is not
installed on your system, you can use the ``find`` command as ``find build/nominal -type f``. If you run a similar
command against the mesh convergence build directory you should see the same set of files repeated once per parameter
set because the workflow definitions are identical for each parameter set.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials/waves_quickstart
   $ tree build/nominal
   build/nominal
   |-- SConscript
   |-- abaqus.rpy
   |-- abaqus.rpy.1
   |-- abaqus.rpy.2
   |-- abaqus_utilities.py
   |-- abaqus_utilities.pyc
   |-- post_processing.py
   |-- rectangle_compression.com
   |-- rectangle_compression.csv
   |-- rectangle_compression.dat
   |-- rectangle_compression.h5
   |-- rectangle_compression.inp
   |-- rectangle_compression.inp.in
   |-- rectangle_compression.msg
   |-- rectangle_compression.odb
   |-- rectangle_compression.prt
   |-- rectangle_compression.sta
   |-- rectangle_compression.stdout
   |-- rectangle_compression_datasets.h5
   |-- rectangle_geometry.cae
   |-- rectangle_geometry.cae.stdout
   |-- rectangle_geometry.jnl
   |-- rectangle_geometry.py
   |-- rectangle_mesh.cae
   |-- rectangle_mesh.inp
   |-- rectangle_mesh.inp.stdout
   |-- rectangle_mesh.jnl
   |-- rectangle_mesh.py
   |-- rectangle_partition.cae
   |-- rectangle_partition.cae.stdout
   |-- rectangle_partition.jnl
   |-- rectangle_partition.py
   |-- stress_strain.csv
   |-- stress_strain.pdf
   `-- stress_strain.pdf.stdout

   0 directories, 35 files

**********************
Workflow Visualization
**********************

.. include:: tutorial_quickstart_visualization_1.txt

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/waves_quickstart
   $ waves visualize nominal --output-file waves_quickstart.png --width=30 --height=6

.. include:: tutorial_quickstart_visualization_2.txt

.. raw:: latex

    \begin{landscape}
        \vspace*{\fill}

.. figure:: waves_quickstart.png
   :align: center
   :width: 100%

.. raw:: latex

        \vspace*{\fill}
    \end{landscape}
