.. _tutorial_abaqus_cae:

####################
Tutorial: Abaqus CAE
####################

While the core tutorials focus on script based, non-interactive workflows, it is possible to mix interactive and
graphical elements into a workflow, too. Interactive tasks remove many of the benefits of a build system, such as large
batch execution (parameter studies) and reproducibility. However, they are sometimes unavoidable.

An example of an unavoidable, non-graphical, interactive task is authentication against access controls like when a user
is required to enter a password. Interactive tasks may also be necessary when the cost of scripting project files is
prohibitively high. For example, a project may require editing binary files where the cost of scripting the edits is not
justified, as when the files undergo whole-sale changes frequently, when the edits are difficult to program and require
significant analyst judgement, or when large, legacy files are relatively static. In particular, proprietary binary
files may be more convenient to edit with the tools provided by the proprietary graphical software, like geometric CAD
files.

When adding interactive elements to a workflow, you can preserve some value of automation and reproducibility by
limiting interactive tasks to the earliest portions of the workflow and putting interactively modified files under
version control. The editing process may be interactive, but preserving the file with version control makes the
downstream workflow reproducible for all project members. To regain the benefits of a build system, the downstream
workflow must still be executable from a command line interface.

This tutorial will cover one possible solution to incorporate the graphical, interactive tasks of Abaqus model creation
in Abaqus CAE with an automated, non-interactive job submission task. Similar solutions are limited by third-party
interfaces, but should be possible in most cases where a scripting interface is available.

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

.. include:: version_check_warning.txt

*******************
Directory Structure
*******************

3. Create the project directory structure and copy the tutorial files into the ``~/waves-tutorials/tutorial_abaqus_cae``
   sub-directory with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

      $ waves fetch tutorials/tutorial_abaqus_cae --destination ~/waves-tutorials/tutorial_abaqus_cae
      WAVES fetch
      Destination directory: '/home/roppenheimer/waves-tutorials/tutorial_abaqus_cae'
      $ cd ~/waves-tutorials/tutorial_abaqus_cae
      $ pwd
      /home/roppenheimer/waves-tutorials/tutorial_abaqus_cae

***************
SConscript File
***************

For this tutorial, we will not discuss the main SCons configuration file named ``SConstruct``, which contains project
setup boilerplate. :ref:`tutorialsconstruct` has a more complete discussion about the contents of the ``SConstruct``
file.

The ``SConscript`` file contains the workflow task definitions. This tutorial contains two sets of tasks. The first set
of tasks prepare the Abaqus CAE cantilever beam model from the tutorials provided by the Abaqus documentation and
retrieved with the ``fetch`` command :cite:`ABAQUS`. These tasks are not strictly part of the tutorial. Instead they
produce a job submission ready ``beam.cae`` file. See the Abaqus manual for a tutorial on using Abaqus CAE.

.. admonition:: tutorial_abaqus_cae/SConscript

    .. literalinclude:: tutorial_abaqus_cae_SConscript
       :language: Python
       :lineno-match:
       :start-after: marker-1
       :end-before: marker-2

The tutorial task is a single Abaqus journal file execution. It should look similar to the journal file tasks introduced
in the core tutorials: :ref:`tutorial_geometry` and :ref:`tutorial_partition_mesh`. You can read more about the behavior
of the ``AbaqusJournal`` builder in the function API :meth:`waves.scons_extensions.abaqus_journal_builder_factory` and the core
tutorials.

.. admonition:: tutorial_abaqus_cae/SConscript

    .. literalinclude:: tutorial_abaqus_cae_SConscript
       :language: Python
       :lineno-match:
       :start-after: marker-2
       :end-before: marker-3

*******************
Abaqus Journal File
*******************

The Abaqus journal file is a small command line utility designed to open job submission ready CAE model files and submit
the simulation. You can read more about journal file design in the core tutorials: :ref:`tutorial_geometry` and
:ref:`tutorial_partition_mesh`. This journal file shares many of the same features, such as docstrings for the API, a
command line interface, default execution values, input file handling to avoid accidental source modification during
workflow execution, and function separation to smaller unit tasks.

.. admonition:: tutorial_abaqus_cae/submit_cae.py

    .. literalinclude:: tutorial_abaqus_cae_submit_cae.py
       :language: Python
       :lineno-match:

After command line utility design, Python coding practices, and the Python style guide, the most unique aspect of this
journal file is the ``return_json_dictionary`` function. This is necessary to convert string based job arguments to
Abaqus scripting objects found in the ``abaqusConstants`` module. In an active modsim project, this function would be
broken into yet smaller units of re-usable work and placed in a shared utilities module as introduced in
:ref:`tutorial_partition_mesh`.

Here it is kept as a limited use function implemented directly in the calling script for the convenience of documenting
this tutorial and maintaining the tutorial suite. See the :ref:`modsim_templates` for examples of more re-usable utility
functions and unit testing.

****************
Building targets
****************

The tutorial may be executed by a single call of the ``submit_beam_cae`` alias. However, to demonstrate the interactive
use of a CAE file, a second alias is provided, ``create_beam_cae``.

First, create the CAE file

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_abaqus_cae
   $ scons create_beam_cae

This intermediate workflow will fetch the ``beamExample.py`` file from the Abaqus tutorial repository with ``abaqus
fetch``, append a CAE model save command, and execute the journal file. The Abaqus tutorial includes job execution with
the name ``beam_tutorial``, so you will see job output in the build directory along with the desired ``beam.cae`` file.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_abaqus_cae
   $ ls build/beam.cae
   build/beam.cae
   $ tree build/
   build/
   |-- SConscript
   |-- abaqus.rpy
   |-- beam.cae
   |-- beam.cae.stdout
   |-- beam.jnl
   |-- beamExample.py
   |-- beam_tutorial.com
   |-- beam_tutorial.dat
   |-- beam_tutorial.inp
   |-- beam_tutorial.log
   |-- beam_tutorial.msg
   |-- beam_tutorial.odb
   |-- beam_tutorial.prt
   `-- beam_tutorial.sta

   0 directories, 14 files

Take some time to open the CAE file and look for familiar CAE model and job data. Since this model is job ready, there
is nothing to edit.

Finally, run the post-interactive workflow that is the subject of this tutorial

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_abaqus_cae
   $ scons submit_beam_cae

This workflow calls the ``submit_cae.py`` journal file to submit the job defined in ``beam.cae``. The new files should
look identical (except for timestamps and job name) to the output produced by the ``beamExample.py`` job.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_abaqus_cae
   $ tree build -P "beam.*"
   build
   |-- beam.cae
   |-- beam.cae.stdout
   |-- beam.com
   |-- beam.dat
   |-- beam.inp
   |-- beam.jnl
   |-- beam.log
   |-- beam.msg
   |-- beam.odb
   |-- beam.odb.stdout
   |-- beam.prt
   `-- beam.sta

   0 directories, 13 files

To better understand the mixed workflow, open the ``build/beam.cae`` file and edit it with Abaqus CAE. When you've
finished editing the file, save it, close Abaqus CAE, and re-run the ``scons submit_beam_cae`` command. Observe the
SCons output during execution and the timestamp changes in the build directory. It should look similar to the example
output below.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_abaqus_cae
   $ scons submit_beam_cae --debug=explain
   scons: Reading SConscript files ...
   Checking whether /apps/abaqus/Commands/abq2024 program exists.../apps/abaqus/Commands/abq2024
   Checking whether abq2024 program exists...no
   scons: done reading SConscript files.
   scons: Building targets ...
   scons: rebuilding `build/beam.odb' because `build/beam.cae' changed
   cd /home/roppenheimer/waves-tutorials/tutorial_abaqus_cae/build && /apps/abaqus/Commands/abq2024 cae -noGui /home/roppenheimer/waves-tutorials/tutorial_abaqus_cae/build/submit_cae.py -- --input-file /home/roppenheimer/waves-tutorials/tutorial_abaqus_cae/build/beam.cae --job-name beam --model-name Beam > /home/roppenheimer/waves-tutorials/tutorial_abaqus_cae/build/beam.odb.stdout 2>&1
   scons: done building targets.

************
Output Files
************

The full output directory should look like the following

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_abaqus_cae
   $ tree build
   build
   |-- SConscript
   |-- abaqus.rpy
   |-- abaqus.rpy.1
   |-- beam.cae
   |-- beam.cae.stdout
   |-- beam.com
   |-- beam.dat
   |-- beam.inp
   |-- beam.jnl
   |-- beam.log
   |-- beam.msg
   |-- beam.odb
   |-- beam.odb.stdout
   |-- beam.prt
   |-- beam.sta
   |-- beamExample.py
   |-- beam_tutorial.com
   |-- beam_tutorial.dat
   |-- beam_tutorial.inp
   |-- beam_tutorial.log
   |-- beam_tutorial.msg
   |-- beam_tutorial.odb
   |-- beam_tutorial.prt
   |-- beam_tutorial.sta
   `-- submit_cae.py

   0 directories, 26 files
