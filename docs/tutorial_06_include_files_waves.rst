.. _tutorial_include_files_waves:

##########################
Tutorial 06: Include Files
##########################

**********
References
**********

* Adding to `PYTHONPATH`_ with `Python sys`_ :cite:`python`
* `Python Modules`_ :cite:`python`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Copy the ``tutorial_05_parameter_substitution`` file to a new file named ``tutorial_06_include_files``

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_05_parameter_substitution tutorial_06_include_files

4. Create a new directory in ``eabm_package/python`` in the ``waves-eabm-tutorial`` directory.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ mkdir -p eabm_package/python

.. _tutorial_include_files_waves_python_parameter_file:

*********************
Python Parameter File
*********************

In this tutorial, we will update the code from :ref:`tutorial_parameter_substitution_waves` to use an included parameter
file instead of hardcoding the parameter definitions in the ``SConscript`` file. This technique will allow parameter
re-use between simulations.

5. Create a new file ``eabm_package/python/single_element_compression_nominal.py`` from the content below.

.. admonition:: waves-eabm-tutorial/eabm_package/python/single_element_compression_nominal.py

   .. literalinclude:: python_single_element_compression_nominal.py
      :language: Python

The file you just created is an exact copy of the code snippet in your ``tutorial_05_parameter_substitution``
file that defines the parameter key-value pairs.

6. Create Python module initialization files to create a project specific local Python package.

.. admonition:: waves-eabm-tutorial/eabm_package/python/__init__.py

   .. code-block::

      $ pwd
      /path/to/waves-eabm-tutorial
      $ touch eabm_package/python/__init__.py
      $ find . -name "__init__.py"
      ./waves-eabm-tutorial/eabm_package/abaqus/__init__.py
      ./waves-eabm-tutorial/eabm_package/python/__init__.py
      ./waves-eabm-tutorial/eabm_package/__init__.py

The ``__init__.py`` files tell Python what directories to treat as a package or module. They need to exist, but do not
need any content. You can read more about `Python Modules`_ in the `Python documentation`_.

.. _tutorials_tutorial_include_files_waves:

**********
SConscript
**********

7. Use the ``diff`` below to make the following modifications to your ``tutorial_06_include_files`` file:

   * Import ``single_element_compression_nominal`` from the ``eabm_package.python`` module
   * Remove the ``simulation_variables`` dictionary that was created in :ref:`tutorial_parameter_substitution_waves`'s
     code
   * Define ``simulation_variables``  using the newly imported ``single_element_compression_nominal`` module

A ``diff`` against the ``SConscript`` file from :ref:`tutorial_parameter_substitution_waves` is included below to help
identify the changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_06_include_files

   .. literalinclude:: tutorials_tutorial_06_include_files
      :language: Python
      :diff: tutorials_tutorial_05_parameter_substitution

The first change to be made is importing the ``single_element_compression_nominal`` module from the
``eabm_package.python`` module you created in the :ref:`tutorial_include_files_waves_python_parameter_file` section of
this tutorial. This import statement will import all variables within the ``single_element_compression_nominal.py`` file
and make them available in the ``SConscript`` file's name space. See the `Python Modules`_ documentation for more
information about importing modules. You can access those variables with the following syntax:

.. code-block:: python

   single_element_compression_nominal.simulation_variables

The second change removes the code that defines ``simulation_variables`` that remained from
:ref:`tutorial_parameter_substitution_waves`'s code.

The final change made in the ``tutorial_06_include_files`` file is to re-define the ``simulation_variables``
from the ``single_element_compression_nominal`` module. The end result at this point in the code is the same between
this tutorial and :ref:`tutorial_parameter_substitution_waves`.  However, now we import variables from a separate file,
list that file as a source dependency of the parameterized targets, and allow ourselves the ability to change parameters
without modification to the ``SConscript`` file.

**********
SConstruct
**********

8. Use the ``diff`` below to modify your ``waves-eabm-tutorial/SConstruct`` file in the following ways:

   * Add the ``waves-eabm-tutorial`` directory to your `PYTHONPATH`_ to make the ``eabm_package`` - and thus
     the modules within it - importable
   * Add ``tutorial_06_include_files`` to the ``workflow_configurations`` list

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_parameter_substitution_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: tutorials_tutorial_06_include_files_SConstruct
      :language: Python
      :diff: tutorials_tutorial_05_parameter_substitution_SConstruct

The first change you made allows for us to import modules from the ``eabm_package`` package. This step is neccessary to
be able to import the ``eabm_package.python`` module in the ``tutorial_06_include_files`` file.

The last change to be made is adding ``tutorial_06_include_files`` to the ``workflow_configurations`` list. This
process should be quite familiar by now.

*************
Build Targets
*************

9. Build the new targets

.. code-block:: bash

    $ pwd
    /path/to/waves-eabm-tutorial
    $ scons tutorial_06_include_files
    scons: Reading SConscript files ...
    Checking whether abq2021 program exists.../apps/abaqus/Commands/abq2021
    Checking whether abq2020 program exists.../apps/abaqus/Commands/abq2020
    scons: done reading SConscript files.
    scons: Building targets ...
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_06_include_files && /apps/abaqus/Commands/abaqus -information
    environment > single_element_geometry.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_06_include_files && /apps/abaqus/Commands/abaqus cae -noGui
    /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_geometry.py -- --width 1.0 --height 1.0 >
    single_element_geometry.stdout 2>&1
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_06_include_files && /apps/abaqus/Commands/abaqus -information
    environment > single_element_partition.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_06_include_files && /apps/abaqus/Commands/abaqus cae -noGui
    /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_partition.py -- --width 1.0 --height 1.0 >
    single_element_partition.stdout 2>&1
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_06_include_files && /apps/abaqus/Commands/abaqus -information
    environment > single_element_mesh.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_06_include_files && /apps/abaqus/Commands/abaqus cae -noGui
    /home/roppenheimer/waves-eabm-tutorial/eabm_package/abaqus/single_element_mesh.py -- --global-seed 1.0 >
    single_element_mesh.stdout 2>&1
    Copy("build/tutorial_06_include_files/single_element_compression.inp.in",
    "eabm_package/abaqus/single_element_compression.inp.in")
    Creating 'build/tutorial_06_include_files/single_element_compression.inp'
    Copy("build/tutorial_06_include_files/assembly.inp", "eabm_package/abaqus/assembly.inp")
    Copy("build/tutorial_06_include_files/boundary.inp", "eabm_package/abaqus/boundary.inp")
    Copy("build/tutorial_06_include_files/field_output.inp", "eabm_package/abaqus/field_output.inp")
    Copy("build/tutorial_06_include_files/materials.inp", "eabm_package/abaqus/materials.inp")
    Copy("build/tutorial_06_include_files/parts.inp", "eabm_package/abaqus/parts.inp")
    Copy("build/tutorial_06_include_files/history_output.inp", "eabm_package/abaqus/history_output.inp")
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_06_include_files && /apps/abaqus/Commands/abaqus -information
    environment > single_element_compression.abaqus_v6.env
    cd /home/roppenheimer/waves-eabm-tutorial/build/tutorial_06_include_files && /apps/abaqus/Commands/abaqus -job
    single_element_compression -input single_element_compression -double both -interactive -ask_delete no >
    single_element_compression.stdout 2>&1
    scons: done building targets.

************
Output Files
************

Explore the contents of the ``build`` directory using the ``tree`` command against the ``build`` directory, as shown
below. Note the usage of the ``-I`` to reduce clutter in the ``tree`` command output.

.. code-block:: bash

    $ pwd
    /home/roppenheimer/waves-eabm-tutorial
    $ tree build/tutorial_06_include_files/
    build/tutorial_06_include_files/
    |-- abaqus.rpy
    |-- abaqus.rpy.1
    |-- abaqus.rpy.2
    |-- assembly.inp
    |-- boundary.inp
    |-- field_output.inp
    |-- history_output.inp
    |-- materials.inp
    |-- parts.inp
    |-- single_element_compression.abaqus_v6.env
    |-- single_element_compression.com
    |-- single_element_compression.dat
    |-- single_element_compression.inp
    |-- single_element_compression.inp.in
    |-- single_element_compression.msg
    |-- single_element_compression.odb
    |-- single_element_compression.prt
    |-- single_element_compression.sta
    |-- single_element_compression.stdout
    |-- single_element_geometry.abaqus_v6.env
    |-- single_element_geometry.cae
    |-- single_element_geometry.jnl
    |-- single_element_geometry.stdout
    |-- single_element_mesh.abaqus_v6.env
    |-- single_element_mesh.cae
    |-- single_element_mesh.inp
    |-- single_element_mesh.jnl
    |-- single_element_mesh.stdout
    |-- single_element_partition.abaqus_v6.env
    |-- single_element_partition.cae
    |-- single_element_partition.jnl
    `-- single_element_partition.stdout

    0 directories, 32 files

The output files for this tutorial are *exactly* the same as those from :ref:`tutorial_parameter_substitution_waves`. As
was mentioned when modifying the :ref:`tutorials_tutorial_include_files_waves` file, the use of an included Python file
to define our parameters provides the same result as when we hard-code the parameters into the ``SConscript`` file. It
is also worth noting that the ``eabm_package/python/single_element_compression_nominal.py`` file did not get copied to
the build directory. Instead, we added the ``eabm_package`` directory to `PYTHONPATH`_. This way we can import the
``single_element_compression_nominal`` module from its source location and remove any need to duplicate source code by
copying files from place to place.
