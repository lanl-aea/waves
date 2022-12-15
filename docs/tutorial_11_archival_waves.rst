.. _tutorial_archival_waves:

##########################
Tutorial 11: Data Archival
##########################

.. include:: wip_warning.txt

The final step of any analysis workflow should be to archive your simulation files used in reporting and documenation,
both input and output files. The archival task is generally performed once at the end of a project and limited to the
final, peer-reviewed simulation results. However, if the task of archiving these files is added to the automated
workflow, it is easier to guarantee that the archived files are in sync with the simulation results. Of course, it's not
enough to produce the archive, it must also be stored somewhere for retrieval by colleagues and the analysis report
audience.

The archive can include compute environment information and repository version information for improved reproducibility.
For the reproducible version number, it is beneficial to use a versioning scheme that includes information from the
project's version control system, e.g. `git`_. The `WAVES`_ project uses `git`_ and `setuptools_scm`_
:cite:`setuptools_scm` to build version numbers with a clean version number that is uniquely tied to a single commit,
e.g. ``1.2.3``, or a version number appended with the short git hash to uniquely identify the project commit. Setting up
git, git tags, and a `setuptools_scm`_ version number is outside the scope of this tutorial, but highly recommended.

**********
References
**********

* `SCons`_ Tar builder :cite:`scons-man`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

*******************
Directory Structure
*******************

3. Copy the ``tutorial_10_regression_testing`` file to a new file named ``tutorial_11_archival``

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ cp tutorial_10_regression_testing tutorial_11_archival

**********
SConscript
**********

A ``diff`` against the ``tutorial_10_regression_testing`` file from :ref:`tutorial_regression_testing_waves` is included
below to help identify the changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/tutorial_11_archival

   .. literalinclude:: tutorials_tutorial_11_archival
      :language: Python
      :diff: tutorials_tutorial_10_regression_testing

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_regression_testing_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: tutorials_tutorial_11_archival_SConstruct
      :language: Python
      :diff: tutorials_tutorial_10_regression_testing_SConstruct

Note that we retrieve the project configuration ``SConstruct`` file name and location with a `Python lambda expression`_
:cite:`python`. In Python 3, you would normally use the ``__file__`` attribute; however, this attribute is not defined
for `SCons`_ configuation files. Instead, we can recover the configuration file name and absolute path with the same
method used in :ref:`tutorial_geometry_waves` and :ref:`tutorial_partition_mesh_waves` for the Abaqus Python 2
journal files. For consistency with the configuration file path, we assume that the parent directory of the
configuration file is the same as the project root directory.

*************
Build Targets
*************

4. Build the archive target. Note that the usual workflow target does not include the archive task because it is not
   required until the project developer is ready to begin final reporting.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_11_archival_archive --jobs=4

************
Output Files
************

The output should look identical to :ref:`tutorial_regression_testing_waves` with the addition of a single ``*.tar``
file. You can inspect the contents of the archive as below.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ find build -name "*.tar.bz2"
   build/tutorial_11_archival/WAVES-EABM-TUTORIAL-0.1.0.tar.bz2
   $ tar -tjf $(find build -name "*.tar.bz2") | grep parameter_set0
   build/tutorial_11_archival/parameter_set0/single_element_geometry.cae
   build/tutorial_11_archival/parameter_set0/single_element_geometry.jnl
   build/tutorial_11_archival/parameter_set0/single_element_geometry.stdout
   build/tutorial_11_archival/parameter_set0/single_element_geometry.abaqus_v6.env
   build/tutorial_11_archival/parameter_set0/single_element_partition.cae
   build/tutorial_11_archival/parameter_set0/single_element_partition.jnl
   build/tutorial_11_archival/parameter_set0/single_element_partition.stdout
   build/tutorial_11_archival/parameter_set0/single_element_partition.abaqus_v6.env
   build/tutorial_11_archival/parameter_set0/single_element_mesh.inp
   build/tutorial_11_archival/parameter_set0/single_element_mesh.cae
   build/tutorial_11_archival/parameter_set0/single_element_mesh.jnl
   build/tutorial_11_archival/parameter_set0/single_element_mesh.stdout
   build/tutorial_11_archival/parameter_set0/single_element_mesh.abaqus_v6.env
   build/tutorial_11_archival/parameter_set0/single_element_compression.inp.in
   build/tutorial_11_archival/parameter_set0/single_element_compression.inp
   build/tutorial_11_archival/parameter_set0/assembly.inp
   build/tutorial_11_archival/parameter_set0/boundary.inp
   build/tutorial_11_archival/parameter_set0/field_output.inp
   build/tutorial_11_archival/parameter_set0/materials.inp
   build/tutorial_11_archival/parameter_set0/parts.inp
   build/tutorial_11_archival/parameter_set0/history_output.inp
   build/tutorial_11_archival/parameter_set0/single_element_compression.sta
   build/tutorial_11_archival/parameter_set0/single_element_compression.stdout
   build/tutorial_11_archival/parameter_set0/single_element_compression.abaqus_v6.env
   build/tutorial_11_archival/parameter_set0/single_element_compression.odb
   build/tutorial_11_archival/parameter_set0/single_element_compression.dat
   build/tutorial_11_archival/parameter_set0/single_element_compression.msg
   build/tutorial_11_archival/parameter_set0/single_element_compression.com
   build/tutorial_11_archival/parameter_set0/single_element_compression.prt
   build/tutorial_11_archival/parameter_set0/single_element_compression.h5
   build/tutorial_11_archival/parameter_set0/single_element_compression_datasets.h5
   build/tutorial_11_archival/parameter_set0/single_element_compression.csv
   build/tutorial_11_archival/parameter_set0/single_element_compression.h5.stdout
