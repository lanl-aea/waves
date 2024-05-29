.. _tutorial_fierro:

################
Tutorial: Fierro
################

.. include:: wip_warning.txt

**********
References
**********

* `Fierro example input`_: Fierro documentation :cite:`fierro,fierro-docs`

***********
Environment
***********

.. warning::

   The Fierro tutorial requires a different compute environment than the other tutorials. The following commands create
   a dedicated environment is created for the use of this tutorial. You can also use your existing tutorial environment
   environment if you add the `FierroMechanics`_ channel and install the ``fierro-cpu`` package.

`SCons`_, `WAVES`_, and `Fierro`_ can be installed in a `Conda`_ environment with the `Conda`_ package manager. See the
`Conda installation`_ and `Conda environment management`_ documentation for more details about using `Conda`_.

1. Create the Fierro tutorials environment if it doesn't exist

   .. code-block::

      $ conda create --name waves-fierro-env --channel fierromechanics --channel conda-forge waves 'scons>=4.6' fierro-cpu

2. Activate the environment

   .. code-block::

      $ conda activate waves-fierro-env

*******************
Directory Structure
*******************

.. include:: tutorial_directory_setup.txt

4. Create a new ``tutorial_fierro`` directory with the ``waves fetch`` command below

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --destination tutorial_fierro tutorials/tutorial_fierro
   $ ls tutorial_fierro
   SConstruct example_input example_input.yaml

5. Make the new ``tutorial_fierro`` directory the current working directory

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ cd tutorial_fierro
   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_fierro
   $ ls
   SConstruct example_input example_input.yaml

**********
SConscript
**********

6. Review the ``SConscript`` file.

The structure has changed enough from the core tutorials that a diff view is not as useful. Instead the contents of the
new SConscript files are duplicated below.

.. admonition:: waves-tutorials/tutorial_fierro/example_input

   .. literalinclude:: tutorial_fierro_example_input
      :language: Python
      :lineno-match:

********************
Fierro Input File(s)
********************

8. Create or review the `Fierro example input`_ file from the contents below :cite:`fierro-docs`

.. admonition:: waves-tutorials/tutorial_fierro/example_input.yaml

   .. literalinclude:: tutorial_fierro_example_input.yaml
      :lineno-match:

**********
SConstruct
**********

Note that Fierro differs from other solvers in the tutorials. Fierro is deployed as a Conda package and is available in
the launching Conda environment. It is still good practice to check if the executable is available and provide helpful
feedback to developers about the excutable status and workflow configuration.

The structure has changed enough from the core tutorials that a diff view is not as useful. Instead the contents of the
SConstruct file is duplicated below.

.. admonition:: waves-tutorials/tutorial_fierro/SConstruct

   .. literalinclude:: tutorial_fierro_SConstruct
      :language: Python

*************
Build Targets
*************

9. Build the new targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_fierro
   $ scons example_input
   scons: Reading SConscript files ...
   Checking whether fierro program exists.../projects/aea_compute/waves-env/bin/fierro
   scons: done reading SConscript files.
   scons: Building targets ...
   cd /projects/kbrindley/w13repos/waves/waves/tutorials/tutorial_fierro/build/example_input && fierro parallel-explicit
   /projects/kbrindley/w13repos/waves/waves/tutorials/tutorial_fierro/build/example_input/example_input.yaml >
   /projects/kbrindley/w13repos/waves/waves/tutorials/tutorial_fierro/build/example_input/example_input.yaml.stdout 2>&1
   scons: done building targets.

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_fierro
   $ tree build/
   build
   `-- example_input
       |-- example_input
       |-- example_input.yaml
       |-- example_input.yaml.stdout
       `-- vtk
           |-- data
           |   |-- VTK0.vtk
           |   |-- VTK1.vtk
           |   |-- VTK2.vtk
           |   |-- VTK3.vtk
           |   `-- VTK4.vtk
           `-- outputs.vtk.series

   3 directories, 9 files
