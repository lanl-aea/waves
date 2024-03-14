.. _tutorial_quinoa:

################
Tutorial: Quinoa
################

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
   box.py flow.q SConstruct SConscript

5. Make the new ``tutorial_quinoa`` directory the current working directory

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ cd tutorial_quinoa
   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_quinoa
   $ ls
   box.py flow.q SConstruct SConscript

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

.. admonition:: waves-tutorials/tutorial_quinoa/flow.q

   .. literalinclude:: tutorial_quinoa_flow.q
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
previous tutorial workflow configurations are no longer available. Only the ``quinoa-local`` and ``quinoa-remote`` workflow
configurations will be found by SCons at execution time.

*************
Build Targets
*************

9. Build the new targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_quinoa
   $ scons quinoa-remote
   scons: Reading SConscript files ...
   Checking whether /apps/Cubit-16.12/cubit program exists.../apps/Cubit-16.12/cubit
   Checking whether cubit program exists.../apps/Cubit-15.8/cubit
   Checking whether sbatch program exists...no
   Sourcing the shell environment with command 'source /projects/cclong/quinoa/loadenv.sh' ...
   Checking whether inciter program exists.../projects/cclong/quinoa/quinoa/build/Main/inciter
   Checking whether /users/cclong/QUINOA/quinoa/buildOS/Main/inciter program exists...no
   Checking whether charmrun program exists.../projects/cclong/quinoa/quinoa/build/Main/charmrun
   Checking whether /users/cclong/QUINOA/quinoa/buildOS/Main/charmrun program exists...no
   scons: done reading SConscript files.
   scons: Building targets ...
   cd /projects//w13repos/waves-quinoa/build && python /homes/roppenheimer/waves-tutorials/tutorial_quinoa/build/box.py --output-file /homes/roppenheimer/waves-tutorials/tutorial_quinoa/build/box.cub --xlength 1.0 --ylength 0.5 --zlength 0.5 > box.stdout 2>&1
   ssh sn-rfe.lanl.gov "mkdir -p /users//WAVES-TUTORIAL/tutorial_quinoa"
   stty: standard input: Inappropriate ioctl for device
   rsync -rlptv /projects//w13repos/waves-quinoa/build/flow.q /homes/roppenheimer/waves-tutorials/tutorial_quinoa/build/box.exo sn-rfe.lanl.gov:/users/roppeheimer/WAVES-TUTORIAL/tutorial_quinoa
   stty: standard input: Inappropriate ioctl for device
   sending incremental file list
   box.exo

   sent 2,936 bytes  received 2,177 bytes  3,408.67 bytes/sec
   total size is 250,497  speedup is 48.99
   ssh sn-rfe.lanl.gov 'cd /users//WAVES-TUTORIAL/tutorial_quinoa && sbatch --wait --output=build/remote.slurm.out --wrap "source /etc/profile.d/modules.sh && module use /usr/projects/hpcsoft/modulefiles/toss3/snow/compiler /usr/projects/hpcsoft/modulefiles/toss3/snow/mpi && module load gcc/9.3.0 openmpi/2.1.2 && cd /users/roppeheimer/WAVES-TUTORIAL/tutorial_quinoa && /users/cclong/QUINOA/quinoa/buildOS/Main/charmrun +p4 /users/cclong/QUINOA/quinoa/buildOS/Main/inciter --verbose --control flow.q --input box.exo > remote.stdout 2>&1"'
   stty: standard input: Inappropriate ioctl for device
   Submitted batch job 6542014
   rsync -rltpv sn-rfe.lanl.gov:/users//WAVES-TUTORIAL/tutorial_quinoa/ /homes/roppenheimer/waves-tutorials/tutorial_quinoa/build
   stty: standard input: Inappropriate ioctl for device
   receiving incremental file list
   ./
   demo.q
   diag
   inciter_input.log
   inciter_screen.log
   mesh.exo
   mesh_edge_pdf.0.txt
   mesh_ntet_pdf.0.txt
   mesh_vol_pdf.0.txt
   out.e-s.0.4.0
   out.e-s.0.4.1
   out.e-s.0.4.2
   out.e-s.0.4.3
   remote.stdout
   build/
   build/remote.slurm.out
   restart/
   restart/MainChares.dat
   restart/RO.dat
   restart/sub0/
   restart/sub0/Chares_0.dat
   restart/sub0/Groups_0.dat
   restart/sub0/Groups_1.dat
   restart/sub0/Groups_2.dat
   restart/sub0/Groups_3.dat
   restart/sub0/NodeGroups_0.dat
   restart/sub0/NodeGroups_1.dat
   restart/sub0/NodeGroups_2.dat
   restart/sub0/NodeGroups_3.dat
   restart/sub0/arr_0.dat
   restart/sub0/arr_1.dat
   restart/sub0/arr_2.dat
   restart/sub0/arr_3.dat

   sent 602 bytes  received 18,552,955 bytes  7,421,422.80 bytes/sec
   total size is 18,796,856  speedup is 1.01
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
   build/
   ├── box.cub
   ├── box.exo
   ├── box.py
   ├── box.stdout
   ├── build
   │   └── remote.slurm.out
   ├── diag
   ├── flow.q
   ├── inciter_input.log
   ├── inciter_screen.log
   ├── mesh_edge_pdf.0.txt
   ├── mesh_ntet_pdf.0.txt
   ├── mesh_vol_pdf.0.txt
   ├── out.e-s.0.1.0
   ├── remote.stdout
   ├── restart
   │   ├── MainChares.dat
   │   ├── RO.dat
   │   └── sub0
   │       ├── arr_0.dat
   │       ├── Chares_0.dat
   │       ├── Groups_0.dat
   │       └── NodeGroups_0.dat
   └── SConscript

   3 directories, 21 files
