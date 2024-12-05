.. _tutorial_quinoa:

################
Tutorial: Quinoa
################

.. include:: wip_warning.txt

.. warning::

   Most WAVES tutorials are used as system tests in the regression test suite to ensure that the tutorial files are
   up-to-date and functional. While the Quinoa team refactors around a breaking change in the input file parser, the
   Quiona tutorial is not part of the regression suite, but the Quinoa builder unit tests are part of the verification
   suite. If you run into problems running this tutorial, please contact the Quiona development team for the current
   status of the input file parser.

.. warning::

   Most WAVES tutorials are used as system tests in the regression test suite to ensure that the tutorial files are
   up-to-date and functional. The ``quinoa-local`` alias *without* sbatch submission is part of the regression suite,
   but neither the sbatch submission nor the ``quinoa-remote`` alias is regression tested. The SSH remote excution and
   sbatch behavior was tested when the tutorial was written and is expected to run correctly. If you run into problems
   running this tutorial, please contact the WAVES development team.

**********
References
**********

* `Cubit`_: Python Interface :cite:`cubit`
* `Cubit`_: Importing Cubit into Python :cite:`cubit`
* `Quinoa`_: Quinoa documentation :cite:`quinoa,quinoa-docs`
* `Charm++`_ :cite:`charmplusplus`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

.. include:: tutorial_directory_setup.txt

4. Create a new ``tutorial_quinoa`` directory with the ``waves fetch`` command below

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --destination tutorial_quinoa tutorials/tutorial_quinoa
   $ ls tutorial_quinoa
   box.py flow.lua SConstruct SConscript

5. Make the new ``tutorial_quinoa`` directory the current working directory

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ cd tutorial_quinoa
   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_quinoa
   $ ls
   box.py flow.lua SConstruct SConscript

**********
SConscript
**********

6. Review the ``SConscript`` file.

The structure has changed enough from the core tutorials that a diff view is not as useful. Instead the contents of the
new SConscript files are duplicated below.

.. admonition:: waves-tutorials/tutorial_quinoa/SConscript

   .. literalinclude:: tutorial_quinoa_SConscript
      :language: Python
      :lineno-match:

*******************
Cubit Journal Files
*******************

7. Review the ``box.py`` Cubit journal file

The Cubit journal file includes a similar CLI introduced in :ref:`tutorial_partition_mesh` for the Abaqus journal
files. Besides the differences in Abaqus and Cubit commands, the major difference between the Abaqus and Cubit journal
files is the opportunity to use Python 3 with Cubit, where Abaqus journal files must use the Abaqus controlled
installation of Python 2. Unlike the core tutorials, this journal file only parameterizes the geometry, so intermediate
partition and mesh journal files are not as useful and the journal file performs all operations at once.

.. admonition:: waves-tutorials/tutorial_quinoa/box.py

   .. literalinclude:: tutorial_quinoa_box.py
       :language: Python
       :lineno-match:

********************
Quinoa Input File(s)
********************

8. Create or review the Quinoa input file from the contents below

.. admonition:: waves-tutorials/tutorial_quinoa/flow.lua

   .. literalinclude:: tutorial_quinoa_flow.lua
      :lineno-match:

**********
SConstruct
**********

Note that Quinoa requires a separate construction environment from the launching Conda environment. This is because the
Quinoa compiler/linker and openmpi library conflict with the launching Conda environment. You may need to update the
Quinoa activation shell command according to the instructions on your local system.

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_simulation` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/tutorial_quinoa/SConstruct

   .. literalinclude:: tutorial_quinoa_SConstruct
      :language: Python
      :diff: tutorials_tutorial_04_simulation_SConstruct

Note that the Cubit Python file doesn't perform any imports from the current modsim project package, so the
``PYTHONPATH`` modification is no longer required. This tutorial is created in a new, stand-alone subdirectory, so the
previous tutorial workflow configurations are no longer available. Only the ``quinoa-local`` and ``quinoa-remote``
workflow configurations will be found by SCons at execution time.

*************
Build Targets
*************

9. Build the new targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_quinoa
   scons: Reading SConscript files ...
   Checking whether '/apps/Cubit-16.12/cubit' program exists.../apps/Cubit-16.12/cubit
   Checking whether 'cubit' program exists...no
   Checking whether 'sbatch' program exists...no
   Sourcing the shell environment with command 'module use /projects/aea_compute/modulefiles && module load aea-quinoa' ...
   Checking whether 'inciter' program exists.../projects/aea_compute/aea-quinoa/bin/inciter
   Checking whether '/users/cclong/QUINOA/quinoa/buildOS/Main/inciter' program exists...no
   Checking whether 'charmrun' program exists.../projects/aea_compute/aea-quinoa/bin/charmrun
   Checking whether '/users/cclong/QUINOA/quinoa/buildOS/Main/charmrun' program exists...no
   scons: done reading SConscript files.
   scons: Building targets ...
   cd /home/roppenheimer/waves-tutorials/tutorial_quinoa/build && python /home/roppenheimer/waves-tutorials/tutorial_quinoa/build/box.py --output-file /home/roppenheimer/waves-tutorials/tutorial_quinoa/build/box.cub --xlength 1.0 --ylength 0.5 --zlength 0.5 > /home/roppenheimer/waves-tutorials/tutorial_quinoa/build/box.cub.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_quinoa/build && /projects/aea_compute/aea-quinoa/bin/charmrun +p1 /projects/aea_compute/aea-quinoa/bin/inciter --control /home/roppenheimer/waves-tutorials/tutorial_quinoa/build/flow.lua --input /home/roppenheimer/waves-tutorials/tutorial_quinoa/build/box.exo > /home/roppenheimer/waves-tutorials/tutorial_quinoa/build/local.stdout 2>&1
   scons: done building targets.

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_quinoa
   $ tree build/
   build
   |-- SConscript
   |-- box.cub
   |-- box.cub.stdout
   |-- box.exo
   |-- box.py
   |-- diag
   |-- flow.lua
   |-- flow.q
   |-- inciter_input.log
   |-- inciter_screen.log
   |-- local.stdout
   |-- mesh_edge_pdf.0.txt
   |-- mesh_ntet_pdf.0.txt
   |-- mesh_vol_pdf.0.txt
   |-- out.e-s.0.1.0
   `-- restart
       |-- MainChares.dat
       |-- RO.dat
       `-- sub0
           |-- Chares_0.dat
           |-- Groups_0.dat
           |-- NodeGroups_0.dat
           `-- arr_0.dat

   2 directories, 21 files
