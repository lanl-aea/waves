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

.. include:: tutorial_quickstart_build_1.txt

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

.. include:: tutorial_quickstart_build_2.txt

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_gmsh
   $ ls build/nominal/stress_strain.pdf
   build/nominal/stress_strain.pdf

.. figure:: tutorial_gmsh_stress_strain.png
   :align: center
   :width: 50%

.. include:: tutorial_quickstart_build_3.txt

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

.. include:: tutorial_quickstart_build_4.txt

************
Output Files
************

Explore the contents of the ``build`` directory using the ``find`` command against the ``build`` directory, as shown
below.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials/tutorial_gmsh
   $ find build/nominal -type f
   build/nominal/SConscript
   build/nominal/__pycache__/vtu2xarray.cpython-312.pyc
   build/nominal/post_processing.py
   build/nominal/rectangle.py
   build/nominal/rectangle_compression.01.vtu
   build/nominal/rectangle_compression.02.vtu
   build/nominal/rectangle_compression.03.vtu
   build/nominal/rectangle_compression.04.vtu
   build/nominal/rectangle_compression.05.vtu
   build/nominal/rectangle_compression.06.vtu
   build/nominal/rectangle_compression.07.vtu
   build/nominal/rectangle_compression.08.vtu
   build/nominal/rectangle_compression.09.vtu
   build/nominal/rectangle_compression.10.vtu
   build/nominal/rectangle_compression.12d
   build/nominal/rectangle_compression.cvg
   build/nominal/rectangle_compression.dat
   build/nominal/rectangle_compression.frd
   build/nominal/rectangle_compression.frd.stdout
   build/nominal/rectangle_compression.h5
   build/nominal/rectangle_compression.h5.stdout
   build/nominal/rectangle_compression.inp
   build/nominal/rectangle_compression.inp.in
   build/nominal/rectangle_compression.pvd
   build/nominal/rectangle_compression.sta
   build/nominal/rectangle_compression.vtu.stdout
   build/nominal/rectangle_gmsh.inp
   build/nominal/rectangle_gmsh.inp.stdout
   build/nominal/rectangle_mesh.inp
   build/nominal/rectangle_mesh.inp.stdout
   build/nominal/spooles.out
   build/nominal/stress_strain.csv
   build/nominal/stress_strain.pdf
   build/nominal/stress_strain.pdf.stdout
   build/nominal/stress_strain.png
   build/nominal/stress_strain.png.stdout
   build/nominal/strip_heading.py
   build/nominal/time_points.inp
   build/nominal/vtu2xarray.py

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
