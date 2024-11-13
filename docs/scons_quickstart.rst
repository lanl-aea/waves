.. _scons_quickstart:

################
SCons Quickstart
################

.. include:: scons_tutorial_introduction.txt

**********
References
**********

* `SCons Builders`_ :cite:`scons-user`

***********
Environment
***********

.. include:: scons_tutorial_environment.txt

*******************
Directory Structure
*******************

3. Create the project directory structure and copy the `SCons quickstart source files`_ into the ``~/waves-tutorials/scons_quickstart``
   sub-directory with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

      $ waves fetch tutorials/scons_quickstart --destination ~/waves-tutorials/scons_quickstart
      WAVES fetch
      Destination directory: '/home/roppenheimer/waves-tutorials/scons_quickstart'
      $ cd ~/waves-tutorials/scons_quickstart
      $ pwd
      /home/roppenheimer/waves-tutorials/scons_quickstart

**********
SConscript
**********

For this quickstart, we will not discuss the main SCons configuration file, named ``SConstruct``, which contains project
setup boilerplate. :ref:`tutorialsconstruct` has a more complete discussion about the contents of the ``SConstruct``
file.

The ``SConscript`` file below contains the workflow task definitions. Review the source and target
files defining the workflow tasks. As discussed in :ref:`build_system`, a task definition also requires an action.

.. admonition:: scons_quickstart/SConscript

    .. literalinclude:: scons_quickstart_SConscript
       :language: Python
       :lineno-match:

****************
Building targets
****************

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/scons_quickstart
   $ scons rectangle

************
Output Files
************

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials/scons_quickstart
   $ tree build/
   build/
   |-- SConscript
   |-- abaqus.rpy
   |-- abaqus.rpy.1
   |-- abaqus.rpy.2
   |-- abaqus_utilities.py
   |-- abaqus_utilities.pyc
   |-- rectangle_compression.com
   |-- rectangle_compression.dat
   |-- rectangle_compression.inp
   |-- rectangle_compression.msg
   |-- rectangle_compression.odb
   |-- rectangle_compression.prt
   |-- rectangle_compression.sta
   |-- rectangle_geometry.cae
   |-- rectangle_geometry.jnl
   |-- rectangle_geometry.py
   |-- rectangle_mesh.cae
   |-- rectangle_mesh.inp
   |-- rectangle_mesh.jnl
   |-- rectangle_mesh.py
   |-- rectangle_partition.cae
   |-- rectangle_partition.jnl
   `-- rectangle_partition.py

   0 directories, 23 files

**********************
Workflow Visualization
**********************

While SCons is a powerful build automation tool, it does not come with a built-in visualization
feature for displaying your build workflow. To address this limitation, the |PROJECT| :ref:`waves_visualize_cli`
command can be used.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/scons_quickstart
   $ waves visualize rectangle --output-file scons_quickstart.png --width=28 --height=6

.. raw:: latex

    \begin{landscape}
        \vspace*{\fill}

.. figure:: scons_quickstart.png
   :align: center
   :width: 100%

.. raw:: latex

        \vspace*{\fill}
    \end{landscape}
