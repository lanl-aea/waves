#############
WAVES-Truchas
#############

Developing early prototype for WAVES of Truchas: https://gitlab.com/truchas/truchas.

***********
Environment
***********

Truchas local-build
===================

If you have a local build of Truchas, you can install everything except Truchas with Conda.

.. code-block::

   $ conda create --name waves-truchas --file environment.txt --channel conda-forge
   $ conda activate waves-truchas

You will need to pass the absolute path to the Truchas executable to the SCons project configuration for every
execution.

.. code-block::

   $ scons --truchas-command=/path/to/excutable/truchas

You may also edit the ``SConstruct`` file's default Truchas path options. This is a preference ordered list. All paths
will be searched, but the first found is used to run simulations.

.. code-block::

   default_truchas_commands = [
       "/path/to/executable/truchas",
       "truchas",
   ]


Truchas conda-package installation
==================================

If you have a conda-package deployment of Truchas available, you can install all dependencies with Conda.

.. code-block::

   $ conda create --name waves-truchas --file environment.txt truchas --channel /my/channel/with/truchas --channel conda-forge
   $ conda create --name waves-truchas --file environment.txt truchas --channel /projects/aea_compute/aea-conda --channel conda-forge
   $ conda create --name waves-truchas --file environment.txt truchas --channel /Users/roppenheimer/Documents/aea-conda --channel conda-forge

You can create a local Conda channel to use for environment creation. See the Conda documentation:
https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/create-custom-channels.html.

*******************
Running simulations
*******************

Show available workflows

.. code-block::

   $ scons -h

Simple execution if the Truchas executable is found by the ``SConstruct`` default search paths.

.. code-block::

   $ scons nominal

Example build directory expectations for ``nominal`` workflow

.. code-block::

   (waves-truchas) [roppenheimer@host waves-truchas]% find build -type f
   build/nominal/SConscript
   build/nominal/cube_compression.inp
   build/nominal/cube_compression.inp.in
   build/nominal/cube_compression/cube_compression.h5
   build/nominal/cube_compression/cube_compression.log
   build/nominal/cube_compression/cube_compression.log.stdout
   build/nominal/cube_geometry.cub
   build/nominal/cube_geometry.cub.stdout
   build/nominal/cube_geometry.py
   build/nominal/cube_mesh.cub
   build/nominal/cube_mesh.g
   build/nominal/cube_mesh.g.stdout
   build/nominal/cube_mesh.py
   build/nominal/cube_partition.cub
   build/nominal/cube_partition.cub.stdout
   build/nominal/cube_partition.py
   build/parameter_studies/mesh_convergence.h5

If you need to specify an absolute path to your local Truchas executable

.. code-block::

   $ scons nominal --truchas-command=/path/to/executable/truchas

Trouble-shooting task definitions that rebuild when you don't expect it.

.. code-block::

   $ scons nominal --truchas-command=/path/to/executable/truchas --debug=explain

Build all workflows

.. code-block::

   $ scons .

******************
Adding simulations
******************

#. Copy the input file(s) to the project root directory.
#. Add a new simulation task definition to ``SConscript`` following the existing pattern. Be sure to include all
   required source files and expected output files explicitly.
#. Add a new project alias following the existing pattern. The current naming convention is to use the root input file's
   basename.
