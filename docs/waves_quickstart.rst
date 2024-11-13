.. _waves_quickstart:

####################
|PROJECT| Quickstart
####################

This quickstart will create a minimal, two file project configuration combining elements of the tutorials listed below.

* :ref:`tutorialsconstruct`
* :ref:`tutorial_geometry`
* :ref:`tutorial_partition_mesh`
* :ref:`tutorial_solverprep`
* :ref:`tutorial_simulation`
* :ref:`tutorial_parameter_substitution`
* :ref:`tutorial_cartesian_product`
* :ref:`tutorial_post_processing`

These tutorials and this quickstart describe the computational engineering workflow through simulation execution and
post-processing. This tutorial will use a different working directory and directory structure than the rest of the
tutorials to avoid filename clashes.

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

***************
SConscript File
***************

For this quickstart, we will not discuss the main SCons configuration file named SConstruct, which contains project
setup boilerplate. :ref:`tutorialsconstruct` has a more complete discussion about the contents of the
``SConstruct`` file.

The ``SConscript`` file below contains the workflow task definitions. Review the source and target files defining the
workflow tasks. As discussed in :ref:`build_system`, a task definition also requires an action.  For convenience,
|PROJECT| provides builders for common engineering software with pre-defined task actions.  See the
:meth:`waves.scons_extensions.abaqus_journal_builder_factory` and :meth:`waves.scons_extensions.abaqus_solver` for more
complete descriptions of the builder actions.

.. admonition:: waves_quickstart/SConscript

    .. literalinclude:: waves_quickstart_SConscript
       :language: Python
       :lineno-match:

****************
Building targets
****************

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/waves_quickstart
   $ scons nominal

************
Output Files
************

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
   |-- rectangle_compression.abaqus_v6.env
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

   0 directories, 36 files

**********************
Workflow Visualization
**********************

To visualize the workflow, you can use the |project| :ref:`waves_visualize_cli` command. The ``--output-file`` allows
you to save the visualization file non-interactively. Without this option, you'll enter an interactive matplotlib window.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/waves_quickstart
   $ waves visualize nominal --output-file waves_quickstart.png --width=30 --height=6

The workflow visualization should look similar to the image below, which is a representation of the directed graph
constructed by `SCons`_ from the task definitions. The image starts with the final workflow target on the left, in this
case the ``nominal`` simulation target alias. Moving left to right, the files required to complete the workflow are
shown until we reach the original source file(s) on the far right of the image. The arrows represent actions and are
drawn from a required source to the produced target. The :ref:`computational_tools` introduction discusses the
relationship of a :ref:`build_system` task and :ref:`build_system_directed_graphs`.

.. raw:: latex

    \begin{landscape}
        \vspace*{\fill}

.. figure:: waves_quickstart.png
   :align: center
   :width: 100%

.. raw:: latex

        \vspace*{\fill}
    \end{landscape}
