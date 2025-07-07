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

   .. only:: not epub

      .. tab-set::
         :sync-group: OS

         .. tab-item:: Linux/MacOS
            :sync: bash

            .. code-block::

               $ conda create --name waves-gmsh-env --channel conda-forge waves 'scons>=4.6' python-gmsh calculix 'ccx2paraview>=3.2' meshio

         .. tab-item:: Windows
            :sync: powershell

            .. code-block::

               PS > conda create --name waves-gmsh- --channel conda-forge waves scons python-gmsh calculix ccx2paraview meshio

2. Activate the environment

   .. only:: not epub

      .. tab-set::
         :sync-group: OS

         .. tab-item:: Linux/MacOS
            :sync: bash

            .. code-block::

               $ conda activate waves-gmsh-env

         .. tab-item:: Windows
            :sync: powershell

            .. code-block::

               PS > conda activate waves-gmsh-env

.. include:: version_check_warning.txt

*******************
Directory Structure
*******************

.. include:: tutorial_directory_setup.txt

3. Create a new ``tutorial_gmsh`` directory with the ``waves fetch`` command below

.. only:: not epub

   .. tab-set::
      :sync-group: OS

      .. tab-item:: Linux/MacOS
         :sync: bash

         .. code-block:: bash

            $ waves fetch tutorials/tutorial_gmsh --destination ~/waves-tutorials/tutorial_gmsh
            WAVES fetch
            Destination directory: '/home/roppenheimer/waves-tutorials/tutorial_gmsh'
            $ cd ~/waves-tutorials/tutorial_gmsh
            $ pwd
            /home/roppenheimer/waves-tutorials/tutorial_gmsh
            $ ls .
            environment.yml  post_processing.py  rectangle_compression.inp.in  rectangle.py  SConscript  SConstruct  strip_heading.py  time_points.inp  vtu2xarray.py

      .. tab-item:: Windows
         :sync: powershell

         .. code-block:: powershell

            PS > waves fetch tutorials\tutorial_gmsh --destination $HOME\waves-tutorials\tutorial_gmsh
            WAVES fetch
            Destination directory: 'C:\Users\roppenheimer\waves-tutorials\tutorial_gmsh'
            PS > Set-Location $HOME\waves-tutorials\tutorial_gmsh
            PS > Get-Location

            Path
            ----
            C:\Users\roppenheimer\waves-tutorials\tutorial_gmsh

            PS > Get-ChildItem .

                Directory: C:\Users\roppenheimer\waves-tutorials\tutorial_gmsh

            Mode                 LastWriteTime         Length Name
            ----                 -------------         ------ ----
            -a---            6/9/2023  4:32 PM            329 environment.yml
            -a---            6/9/2023  4:32 PM           9250 post_processing.py
            -a---            6/9/2023  4:32 PM            498 rectangle_compression.inp.in
            -a---            6/9/2023  4:32 PM           5818 rectangle.py
            -a---            6/9/2023  4:32 PM           2280 SConscript
            -a---            6/9/2023  4:32 PM           3073 SConstruct
            -a---            6/9/2023  4:32 PM           1206 strip_heading.py
            -a---            6/9/2023  4:32 PM             44 time_points.inp
            -a---            6/9/2023  4:32 PM           6079 vtu2xarray.py

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

.. only:: not epub

   .. tab-set::
      :sync-group: OS

      .. tab-item:: Linux/MacOS
         :sync: bash

         .. code-block::

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

      .. tab-item:: Windows
         :sync: powershell

         .. code-block::

            PS > Get-Location

            Path
            ----
            C:\Users\roppenheimer\waves-tutorials\tutorial_gmsh

            PS > scons nominal
            scons: Reading SConscript files ...
            Checking whether 'ccx' program exists...C:\Users\oppenheimer\AppData\Local\miniconda3\envs\waves-gmsh-env\Library\bin\ccx.EXE
            Checking whether 'ccx2paraview' program exists...C:\Users\oppenheimer\AppData\Local\miniconda3\envs\waves-gmsh-env\Scripts\ccx2paraview.EXE
            scons: done reading SConscript files.
            scons: Building targets ...
            Copy("build\nominal\rectangle_compression.inp.in", "rectangle_compression.inp.in")
            Creating 'build\nominal\rectangle_compression.inp'
            cd C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal && python C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle.py --output-file=C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_gmsh.inp > C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_gmsh.inp.stdout 2>&1
            cd C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal && python C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\strip_heading.py --input-file=C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_gmsh.inp --output-file=C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_mesh.inp > C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_mesh.inp.stdout 2>&1
            cd C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal && C:\Users\oppenheimer\AppData\Local\miniconda3\envs\waves-gmsh-env\Library\bin\ccx.EXE -i rectangle_compression > C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_compression.frd.stdout 2>&1
            cd C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal && ccx2paraview C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_compression.frd vtu > C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_compression.vtu.stdout 2>&1
            cd C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal && python C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\vtu2xarray.py --input-file C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_compression.01.vtu C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_compression.02.vtu C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_compression.03.vtu C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_compression.04.vtu C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_compression.05.vtu C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_compression.06.vtu C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_compression.07.vtu C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_compression.08.vtu C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_compression.09.vtu C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_compression.10.vtu --output-file C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_compression.h5 --time-points-file C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\time_points.inp > C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_compression.h5.stdout 2>&1
            cd C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal && python C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\post_processing.py --input-file C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_compression.h5 --output-file C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\stress_strain.pdf --x-units mm/mm --y-units MPa > C:\Users\oppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\stress_strain.pdf.stdout 2>&1
            scons: done building targets.

.. include:: tutorial_quickstart_build_2.txt

.. only:: not epub

   .. tab-set::
      :sync-group: OS

      .. tab-item:: Linux/MacOS
         :sync: bash

         .. code-block::

            $ pwd
            /home/roppenheimer/waves-tutorials/tutorial_gmsh
            $ ls build/nominal/stress_strain.pdf
            build/nominal/stress_strain.pdf

      .. tab-item:: Windows
         :sync: powershell

         .. code-block::

            PS > Get-Location

            Path
            ----
            C:\Users\roppenheimer\waves-tutorials\tutorial_gmsh

            PS > Get-ChildItem build\nominal\stress_strain.pdf

                Directory: C:\Users\roppenheimer\waves-tutorials\tutorial_gmsh\build\nominal

            Mode                 LastWriteTime         Length Name
            ----                 -------------         ------ ----
            -a---            6/9/2023  4:32 PM          12951 stress_strain.pdf

.. figure:: tutorial_gmsh_stress_strain.png
   :align: center
   :width: 50%

.. include:: tutorial_quickstart_build_3.txt

.. only:: not epub

   .. tab-set::
      :sync-group: OS

      .. tab-item:: Linux/MacOS
         :sync: bash

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

      .. tab-item:: Windows
         :sync: powershell

         .. code-block::

            PS > Get-Location

            Path
            ----
            C:\Users\roppenheimer\waves-tutorials\tutorial_gmsh

            PS > Remove-Item build\nominal\rectangle_mesh.inp
            PS > scons nominal
            scons: Reading SConscript files ...
            Checking whether 'ccx' program exists...C:\Users\roppenheimer\AppData\Local\miniconda3\envs\waves-gmsh-env\Library\bin\ccx.EXE
            Checking whether 'ccx2paraview' program exists...C:\Users\roppenheimer\AppData\Local\miniconda3\envs\waves-gmsh-env\Scripts\ccx2paraview.EXE
            scons: done reading SConscript files.
            scons: Building targets ...
            cd C:\Users\roppenheimer\waves-tutorials\tutorial_gmsh\build\nominal && python C:\Users\roppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\strip_heading.py --input-file=C:\Users\roppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_gmsh.inp --output-file=C:\Users\roppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_mesh.inp > C:\Users\roppenheimer\waves-tutorials\tutorial_gmsh\build\nominal\rectangle_mesh.inp.stdout 2>&1
            scons: `nominal' is up to date.
            scons: done building targets.

.. include:: tutorial_quickstart_build_4.txt

************
Output Files
************

Explore the contents of the ``build`` directory, as shown below.

.. only:: not epub

   .. tab-set::
      :sync-group: OS

      .. tab-item:: Linux/MacOS
         :sync: bash

         .. code-block:: bash

            $ pwd
            /home/roppenheimer/waves-tutorials/tutorial_gmsh
            $ find build/nominal -type f
            build/nominal/SConscript
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

      .. tab-item:: Windows
         :sync: powershell

         .. code-block:: powershell

            PS > Get-Location

            Path
            ----
            C:\Users\roppenheimer\waves-tutorials\tutorial_gmsh

            PS > Get-ChildItem -Path build\nominal -Recurse -File

                Directory: C:\Users\roppenheimer\waves-tutorials\tutorial_gmsh\build\nominal

            Mode                 LastWriteTime         Length Name
            ----                 -------------         ------ ----
            -a---            6/9/2023  4:32 PM           9250 post_processing.py
            -a---            6/9/2023  4:32 PM           5405 rectangle_compression.01.vtu
            -a---            6/9/2023  4:32 PM           5485 rectangle_compression.02.vtu
            -a---            6/9/2023  4:32 PM           5415 rectangle_compression.03.vtu
            -a---            6/9/2023  4:32 PM           5475 rectangle_compression.04.vtu
            -a---            6/9/2023  4:32 PM           5399 rectangle_compression.05.vtu
            -a---            6/9/2023  4:32 PM           5384 rectangle_compression.06.vtu
            -a---            6/9/2023  4:32 PM           5387 rectangle_compression.07.vtu
            -a---            6/9/2023  4:32 PM           5460 rectangle_compression.08.vtu
            -a---            6/9/2023  4:32 PM           5338 rectangle_compression.09.vtu
            -a---            6/9/2023  4:32 PM           5338 rectangle_compression.10.vtu
            -a---            6/9/2023  4:32 PM            255 rectangle_compression.12d
            -a---            6/9/2023  4:32 PM           1938 rectangle_compression.cvg
            -a---            6/9/2023  4:32 PM              0 rectangle_compression.dat
            -a---            6/9/2023  4:32 PM          24021 rectangle_compression.frd
            -a---            6/9/2023  4:32 PM          15815 rectangle_compression.frd.stdout
            -a---            6/9/2023  4:32 PM          19463 rectangle_compression.h5
            -a---            6/9/2023  4:32 PM           9040 rectangle_compression.h5.stdout
            -a---            6/9/2023  4:32 PM            489 rectangle_compression.inp
            -a---            6/9/2023  4:32 PM            498 rectangle_compression.inp.in
            -a---            6/9/2023  4:32 PM            783 rectangle_compression.pvd
            -a---            6/9/2023  4:32 PM            830 rectangle_compression.sta
            -a---            6/9/2023  4:32 PM           5388 rectangle_compression.vtu.stdout
            -a---            6/9/2023  4:32 PM            434 rectangle_gmsh.inp
            -a---            6/9/2023  4:32 PM            886 rectangle_gmsh.inp.stdout
            -a---            6/9/2023  4:32 PM            343 rectangle_mesh.inp
            -a---            6/9/2023  4:32 PM            252 rectangle_mesh.inp.stdout
            -a---            6/9/2023  4:32 PM           5818 rectangle.py
            -a---            6/9/2023  4:32 PM           2280 SConscript
            -a---            6/9/2023  4:32 PM              0 spooles.out
            -a---            6/9/2023  4:32 PM           1014 stress_strain.csv
            -a---            6/9/2023  4:32 PM          12951 stress_strain.pdf
            -a---            6/9/2023  4:32 PM           1055 stress_strain.pdf.stdout
            -a---            6/9/2023  4:32 PM           1206 strip_heading.py
            -a---            6/9/2023  4:32 PM             44 time_points.inp
            -a---            6/9/2023  4:32 PM           6079 vtu2xarray.py

**********************
Workflow Visualization
**********************

.. include:: tutorial_quickstart_visualization_1.txt

.. only:: not epub

   .. tab-set::
      :sync-group: OS

      .. tab-item:: Linux/MacOS
         :sync: bash

         .. code-block::

            $ pwd
            /home/roppenheimer/waves-tutorials/tutorial_gmsh
            $ waves visualize nominal --output-file tutorial_gmsh.png --width=30 --height=6

      .. tab-item:: Windows
         :sync: powershell

         .. code-block::

            PS > Get-Location

            Path
            ----
            C:\Users\roppenheimer\waves-tutorials\tutorial_gmsh

            PS > waves visualize nominal --output-file tutorial_gmsh.png --width=30 --height=6

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
