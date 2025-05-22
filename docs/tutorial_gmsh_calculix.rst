.. _tutorial_gmsh_calculix:

#########################
Quickstart: Gmsh+CalculiX
#########################

This tutorial mirrors the Abaqus-based :ref:`waves_quickstart` with a fully open-source, conda-forge workflow. The
geometry is created and meshed with `Gmsh`_. The finite element simulation is performed with `CalculiX`_. Finally, the
data is extracted with `ccx2paraview`_ and `meshio`_ for scripted quantity of interest (QoI) calculations and
post-processing.

This quickstart will create a minimal, two file project configuration combining elements of the tutorials listed below.

* :ref:`tutorialsconstruct`
* :ref:`tutorial_geometry`
* :ref:`tutorial_partition_mesh`
* :ref:`tutorial_solverprep`
* :ref:`tutorial_simulation`
* :ref:`tutorial_parameter_substitution`
* :ref:`tutorial_cartesian_product`
* :ref:`tutorial_data_extraction`
* :ref:`tutorial_post_processing`

These tutorials and this quickstart describe the computational engineering workflow through simulation execution and
post-processing. This tutorial will use a different working directory and directory structure than the rest of the
tutorials to avoid filename clashes. The quickstart also uses a flat directory structure to simplify the project
configuration. Larger projects, like the :ref:`modsim_templates`, may require a hierarchical directory structure to
separate files with identical basenames.

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

4. Review the ``SConscript`` workflow configuration file.

The structure is sufficiently different from the core tutorials that a diff view is not as useful. Instead the contents
of the new SConscript files are duplicated below.

.. admonition:: waves-tutorials/tutorial_gmsh/SConscript

   .. literalinclude:: tutorial_gmsh_SConscript
      :language: Python
      :lineno-match:

******************
Gmsh Python script
******************

5. Review the Gmsh Python script ``rectangle.py``.

The Gmsh script differs from the Abaqus journal files introduced in :ref:`tutorial_partition_mesh`. Besides the
differences in Abaqus and Gmsh commands, one major difference between the Abaqus and Gmsh scripts is the
opportunity to use Python 3 with Gmsh, where Abaqus journal files must use the Abaqus controlled installation of Python
2. The Gmsh script creates the geometry, partition (sets), and mesh in a single script because the output formats used
by Gmsh can not contain both the geometry definition and the mesh information.

.. admonition:: waves-tutorials/tutorial_gmsh/rectangle.py

   .. literalinclude:: tutorial_gmsh_rectangle.py
       :language: Python
       :lineno-match:

The other Python scripts will not be discussed in detail. They are small content handling and data conversion utilities
or discussed in greater depth in other tutorials.

*******************
CalculiX Input File
*******************

6. Create or review the `CalculiX`_ input file from the contents below

.. admonition:: waves-tutorials/tutorial_gmsh/rectangle_compression.inp

   .. literalinclude:: tutorial_gmsh_rectangle_compression.inp
      :lineno-match:

**********
SConstruct
**********

Note that CalculiX differs from other solvers in the tutorials. CalculiX is deployed as a Conda package and is available in
the launching Conda environment. It is still good practice to check if the executable is available and provide helpful
feedback to developers about the excutable status and workflow configuration.

The structure has changed enough from the core tutorials that a diff view is not as useful. Instead the contents of the
SConstruct file is duplicated below.

.. admonition:: waves-tutorials/tutorial_gmsh/SConstruct

   .. literalinclude:: tutorial_gmsh_SConstruct
      :language: Python

*************
Build Targets
*************

7. Build the workflow targets

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials/tutorial_gmsh
   $ scons fierro
   scons: Reading SConscript files ...
   Checking whether 'ccx' program exists.../home/roppenheimer/anaconda3/envs/waves-gmsh-env/bin/ccx
   Checking whether 'ccx2paraview' program exists.../home/roppenheimer/anaconda3/envs/waves-gmsh-env/bin/ccx2paraview
   scons: done reading SConscript files.
   scons: Building targets ...
   cd /home/roppenheimer/waves-tutorials/tutorial_gmsh/build && python /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/rectangle.py --output-file=/home/roppenheimer/waves-tutorials/tutorial_gmsh/build/rectangle_gmsh.inp > /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/rectangle_gmsh.inp.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_gmsh/build && python /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/strip_heading.py --input-file=/home/roppenheimer/waves-tutorials/tutorial_gmsh/build/rectangle_gmsh.inp --output-file=/home/roppenheimer/waves-tutorials/tutorial_gmsh/build/rectangle_mesh.inp > /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/rectangle_mesh.inp.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_gmsh/build && /home/roppenheimer/anaconda3/envs/waves-gmsh-env/bin/ccx -i rectangle_compression > /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/rectangle_compression.frd.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_gmsh/build && ccx2paraview /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/rectangle_compression.frd > /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/rectangle_compression.vtu.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_gmsh/build && python /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/vtu2xarray.py --input-file /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/rectangle_compression.vtu --output-file /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/rectangle_compression.h5 > /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/rectangle_compression.h5.stdout 2>&1
   cd /home/roppenheimer/waves-tutorials/tutorial_gmsh/build && python /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/post_processing.py --input-file /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/rectangle_compression.h5 --output-file stress_strain_comparison.pdf --x-units mm/mm --y-units MPa > /home/roppenheimer/waves-tutorials/tutorial_gmsh/build/stress_strain_comparison.pdf.stdout 2>&1
   scons: done building targets.


************
Output Files
************

Explore the contents of the ``build`` directory using the ``find`` command against the ``build`` directory, as shown
below.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_cubit
   $ find build -type f
   build/rectangle_compression.h5
   build/rectangle_compression.inp
   build/rectangle_compression.h5.stdout
   build/rectangle_compression.sta
   build/rectangle_compression.dat
   build/rectangle_mesh.inp
   build/rectangle_compression.vtu.stdout
   build/rectangle_compression.12d
   build/spooles.out
   build/rectangle_gmsh.inp
   build/rectangle_compression.cvg
   build/stress_strain_comparison.pdf.stdout
   build/rectangle_compression.frd.stdout
   build/rectangle_compression.vtu
   build/rectangle.py
   build/stress_strain_comparison.pdf
   build/post_processing.py
   build/rectangle_gmsh.inp.stdout
   build/SConscript
   build/rectangle_compression.frd
   build/strip_heading.py
   build/vtu2xarray.py
   build/stress_strain_comparison.csv
   build/rectangle_mesh.inp.stdout
