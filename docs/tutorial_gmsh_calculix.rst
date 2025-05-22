.. _tutorial_gmsh_calculix:

#########################
Quickstart: Gmsh+CalculiX
#########################

This tutorial mirrors the Abaqus-based :ref:`waves_quickstart` with a fully open-source, conda-forge workflow. The
geometry is created and meshed with `Gmsh`_. The finite element simulation is performed with `CalculiX`_. Finally, the
data is extracted with `ccx2paraview`_ and `meshio`_ for scripted quantity of interest (QoI) calculations and
post-processing.

.. include:: tutorial_quickstart_introduction.txt

**********
References
**********

* `Gmsh`_ :cite:`gmsh-article,gmsh-webpage`
* `CalculiX`_ :cite:`calculix-webpage`
* `ccx2paraview`_ :cite:`ccx2paraview`
* `meshio`_ :cite:`meshio`

***********
Environment
***********

.. warning::

   The Gmsh+CalculiX tutorial requires a different compute environment than the other tutorials. The following commands
   create a dedicated environment for the use of this tutorial. You can also use your existing tutorial environment with
   the ``conda install`` command while your environment is active.

All of the software required for this tutorial can be installed in a `Conda`_ environment with the `Conda`_ package
manager. See the `Conda installation`_ and `Conda environment management`_ documentation for more details about using
`Conda`_.

1. Create the Gmsh+CalculiX tutorial environment if it doesn't exist

   .. code-block::

      $ conda create --name waves-gmsh-env --channel conda-forge waves 'scons>=4.6' python-gmsh calculix 'ccx2paraview>=3.2' meshio

2. Activate the environment

   .. code-block::

      $ conda activate waves-gmsh-env

.. include:: version_check_warning.txt

*******************
Directory Structure
*******************

.. include:: tutorial_directory_setup.txt

3. Create a new ``tutorial_gmsh`` directory with the ``waves fetch`` command below

.. code-block:: bash

   $ waves fetch tutorials/tutorial_gmsh --destination ~/waves-tutorials/tutorial_gmsh
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials/tutorial_gmsh'
   $ cd ~/waves-tutorials/tutorial_gmsh
   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_gmsh
   $ ls tutorial_gmsh
   SConscript  SConstruct  environment.yml  post_processing.py  rectangle.py  rectangle_compression.inp  strip_heading.py  vtu2xarray.py

**********
SConscript
**********

.. include:: tutorial_quickstart_sconscript.txt

.. admonition:: waves-tutorials/tutorial_gmsh/SConscript

   .. literalinclude:: tutorial_gmsh_SConscript
      :language: Python
      :lineno-match:

**********
SConstruct
**********

.. include:: tutorial_quickstart_sconstruct_1.txt

.. admonition:: waves-tutorials/tutorial_gmsh/SConstruct

    .. literalinclude:: tutorial_gmsh_SConstruct
       :language: Python
       :lineno-match:
       :start-at: # Define parameter studies
       :end-before: # Add workflow(s)

.. include:: tutorial_quickstart_sconstruct_2.txt

.. admonition:: waves-tutorials/tutorial_gmsh/SConstruct

    .. literalinclude:: tutorial_gmsh_SConstruct
       :language: Python
       :lineno-match:
       :start-at: # Add workflow(s)
       :end-before: # List all aliases in help message

.. include:: tutorial_quickstart_sconstruct_3.txt

*************
Build Targets
*************

In ``SConstruct``, the workflows were provided aliases matching the study names for more convenient execution. First,
run the ``nominal`` workflow and observe the task command output as below. The default behavior of `SCons`_ is to report
each task's action as it is executed. |PROJECT| builders capture the STDOUT and STDERR into per-task log files to aid in
troubleshooting and to remove clutter from the terminal output. On first execution you may see a warning message as a
previous parameter study is being requested which will only exist on subsequent executions.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_gmsh
   $ scons nominal
   scons: Reading SConscript files ...
   Checking whether 'ccx' program exists.../projects/aea_compute/waves-env/bin/ccx
   Checking whether 'ccx2paraview' program exists.../projects/aea_compute/waves-env/bin/ccx2paraview
   scons: done reading SConscript files.
   scons: Building targets ...
   Copy("build/nominal/rectangle_compression.inp.in", "rectangle_compression.inp.in")
   Creating 'build/nominal/rectangle_compression.inp'
   cd /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal && python /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle.py --output-file=/home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_gmsh.inp > /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_gmsh.inp.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal && python /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/strip_heading.py --input-file=/home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_gmsh.inp --output-file=/home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_mesh.inp > /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_mesh.inp.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal && /projects/aea_compute/waves-env/bin/ccx -i rectangle_compression > /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_compression.frd.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal && ccx2paraview /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_compression.frd vtu > /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_compression.vtu.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal && python /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/vtu2xarray.py --input-file /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_compression.01.vtu /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_compression.02.vtu /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_compression.03.vtu /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_compression.04.vtu /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_compression.05.vtu /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_compression.06.vtu /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_compression.07.vtu /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_compression.08.vtu /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_compression.09.vtu /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_compression.10.vtu --output-file /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_compression.h5 --time-points-file /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/time_points.inp > /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_compression.h5.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal && python /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/post_processing.py --input-file /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_compression.h5 --output-file /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/stress_strain_comparison.pdf --x-units mm/mm --y-units MPa > /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/stress_strain_comparison.pdf.stdout 2>&1
   scons: done building targets.

You will find the output files in the build directory. The final post-processing image of the uniaxial compression
stress-strain curve is found in ``stress_strain.pdf``.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_gmsh
   $ ls build/nominal/stress_strain.pdf
   build/nominal/stress_strain.pdf

.. figure:: tutorial_gmsh_stress_strain.png
   :align: center
   :width: 50%

Before running the parameter study, explore the conditional re-build behavior of the workflow by deleting the
intermediate output file ``rectangle_mesh.inp`` and re-executing the workflow. You should observe that only the command
which produces the orphan mesh ``rectangle_mesh.inp`` file is re-run. You can confirm by inspecting the time stamps of
files in the build directory before and after file removal and workflow execution.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_gmsh
   $ rm build/nominal/rectangle_mesh.inp
   $ scons nominal
   scons: Reading SConscript files ...
   Checking whether 'ccx' program exists.../projects/aea_compute/waves-env/bin/ccx
   Checking whether 'ccx2paraview' program exists.../projects/aea_compute/waves-env/bin/ccx2paraview
   scons: done reading SConscript files.
   scons: Building targets ...
   cd /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal && python /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/strip_heading.py --input-file=/home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_gmsh.inp --output-file=/home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_mesh.inp > /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/nominal/rectangle_mesh.inp.stdout 2>&1
   scons: `nominal' is up to date.
   scons: done building targets.

You should expect that the geometry and partition tasks do not need to re-execute because their output files still exist
and they are upstream of the mesh task. But the tasks after the mesh task did not re-execute, either. This should be
somewhat surprising. The simulation itself depends on the mesh file, so why didn't the workflow re-execute all tasks
from mesh to post-processing?

Many software build systems, such as `GNU Make`_ use file system modification time stamps to track DAG state
:cite:`gnu-make`. By default the `SCons`_ state machine uses file signatures built from md5 hashes to identify task
state. If the contents of the ``rectangle_mesh.inp`` file do not change, then the md5 signature on re-execution still
matches the build state for the rest of the downstream tasks, which do not need to rebuild.

This default behavior of `SCons`_ makes it desirable for computational science and engineering workflows where
downstream tasks may be computationally expensive. The added cost of computing md5 signatures during configuration is
valuable if it prevents re-execution of a computationally expensive simulation. In actual practice, production
engineering analysis workflows may include tasks and simulations with wall clock run times of hours to days. By
comparison, the cost of using md5 signatures instead of time stamps is often negligible.

Now run the mesh convergence study as below. `SCons`_ uses the ``--jobs`` option to control the number of threads used
in task execution and will run up to 4 tasks simultaneously.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_gmsh
   $ scons mesh_convergence --jobs=4
   ...

The output is truncated, but should look very similar to the ``nominal`` output above, where the primary difference is
that each parameter set is nested one directory lower using the parameter set number.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_gmsh
   $ ls build/mesh_convergence/
   parameter_set0/  parameter_set1/  parameter_set2/  parameter_set3/

These set names are managed by the |PROJECT| parameter study object, which is written to a separate build directory for
later re-execution. This parameter study file is used in the parameter study object construction to identify previously
created parameter sets on re-execution.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_gmsh
   $ ls build/parameter_studies/
   mesh_convergence.h5
   $ waves print_study build/parameter_studies/mesh_convergence.h5
                                           set_hash  width  height  global_seed  displacement
   set_name
   parameter_set0  cf0934b22f43400165bd3d34aa61013f    1.0     1.0        1.000         -0.01
   parameter_set1  ee7d06f97e3dab5010007d57b2a4ee45    1.0     1.0        0.500         -0.01
   parameter_set2  93de452cc9564a549338e87ad98e5288    1.0     1.0        0.250         -0.01
   parameter_set3  49e34595c98442a228efd9e9765f61dd    1.0     1.0        0.125         -0.01

Try adding a new global mesh seed in the middle of the existing range. An example might look
like the following, where the seed ``0.4`` is added between ``0.5`` and ``0.25``.

.. code-block::
   :caption: SConstruct

   mesh_convergence_parameter_generator = waves.parameter_generators.CartesianProduct(
        {
           "width": [1.0],
           "height": [1.0],
           "global_seed": [1.0, 0.5, 0.4, 0.25, 0.125],
           "displacement": [-0.01],
       },
       output_file=mesh_convergence_parameter_study_file,
       previous_parameter_study=mesh_convergence_parameter_study_file
   )

Then re-run the parameter study. The new parameter set should build under the name ``parameter_set4`` and workflow
should build only ``parameter_set4`` tasks. The parameter study file should also be updated in the build directory.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_gmsh
   $ scons mesh_convergence --jobs=4
   $ ls build/mesh_convergence/
   parameter_set0/  parameter_set1/  parameter_set2/  parameter_set3/ parameter_set4/
   $ waves print_study build/parameter_studies/mesh_convergence.h5
                                           set_hash  width  height  global_seed  displacement
   set_name
   parameter_set0  cf0934b22f43400165bd3d34aa61013f    1.0     1.0        1.000         -0.01
   parameter_set1  ee7d06f97e3dab5010007d57b2a4ee45    1.0     1.0        0.500         -0.01
   parameter_set2  93de452cc9564a549338e87ad98e5288    1.0     1.0        0.250         -0.01
   parameter_set3  49e34595c98442a228efd9e9765f61dd    1.0     1.0        0.125         -0.01
   parameter_set4  4a49100665de0220143675c0d6626c50    1.0     1.0        0.400         -0.01

If the parameter study naming convention were managed by hand it would likely be necessary to add the new seed to the
end of the parameter study to guarantee that the new set received a new set number. In practice, parameter studies are
often defined programmatically as a ``range()`` or vary more than one parameter, which makes it difficult to predict how
the set numbers may change. It would be tedious and error-prone to re-number the parameter sets such that the
input/output relationships are consistent. In the best case, mistakes in set re-numbering would result in unnecessary
re-execution of the previous parameter sets. In the worst case, mistakes could result in silent inconsistencies in
the input/output relationships and lead to errors in result interpretations.

|PROJECT| first looks for and opens the previous parameter study file saved in the build directory, reads the previous
set definitions if the file exists, and then merges the previous study definition with the current definition along the
unique set contents identifier coordinate. Under the hood, this unique identifier is an md5 hash of a string
representation of the set contents, which is robust between systems with identical machine precision. To avoid long,
unreadable hashes in build system paths, the unique md5 hashes are tied to the more human readable set numbers seen in
the mesh convergence build directory.

************
Output Files
************

Explore the contents of the ``build`` directory using the ``find`` command against the ``build`` directory, as shown
below.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_cubit
   $ find build/nominal -type f
   build/nominal/rectangle_compression.h5
   build/nominal/rectangle_compression.inp
   build/nominal/rectangle_compression.h5.stdout
   build/nominal/rectangle_compression.sta
   build/nominal/rectangle_compression.dat
   build/nominal/rectangle_mesh.inp
   build/nominal/rectangle_compression.vtu.stdout
   build/nominal/rectangle_compression.12d
   build/nominal/spooles.out
   build/nominal/rectangle_gmsh.inp
   build/nominal/rectangle_compression.cvg
   build/nominal/stress_strain_comparison.pdf.stdout
   build/nominal/rectangle_compression.frd.stdout
   build/nominal/rectangle_compression.vtu
   build/nominal/rectangle.py
   build/nominal/stress_strain_comparison.pdf
   build/nominal/post_processing.py
   build/nominal/rectangle_gmsh.inp.stdout
   build/nominal/SConscript
   build/nominal/rectangle_compression.frd
   build/nominal/strip_heading.py
   build/nominal/vtu2xarray.py
   build/nominal/stress_strain_comparison.csv
   build/nominal/rectangle_mesh.inp.stdout

**********************
Workflow Visualization
**********************

.. include:: tutorial_quickstart_visualization_1.txt

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_gmsh
   $ waves visualize nominal --output-file tutorial_gmsh.png --width=30 --height=6

.. include:: tutorial_quickstart_visualization_2.txt

.. raw:: latex

    \begin{landscape}
        \vspace*{\fill}

.. figure:: tutorial_gmsh.png
   :align: center
   :width: 100%

.. raw:: latex

        \vspace*{\fill}
    \end{landscape}
