.. _tutorial_archival_waves:

##########################
Tutorial 11: Data Archival
##########################

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
* `GNU tar`_ documentation :cite:`gnu-tar`

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
   /path/to/waves-tutorials
   $ cp tutorial_10_regression_testing tutorial_11_archival

**********
SConscript
**********

A ``diff`` against the ``tutorial_10_regression_testing`` file from :ref:`tutorial_regression_testing_waves` is included
below to help identify the changes made in this tutorial.

.. admonition:: waves-tutorials/tutorial_11_archival

   .. literalinclude:: tutorials_tutorial_11_archival
      :language: Python
      :diff: tutorials_tutorial_10_regression_testing

First, we add the new environment keys required by the ``SConscript`` file that will be used by the archive task.
Second, we build a list of all required SCons configuration files for the current workflow, where the
``project_configuration`` will point to the ``SConstruct`` file and by the project's naming convention the build
directory name will match the current ``SConscript`` file name. These SCons workflow configuration files will be
archived with the output of the workflow for reproducibility of the workflow task definitions.

For advanced workflows, e.g. :ref:`tutorial_task_reuse_waves`, that re-use ``SConscript`` files, it may
be necessary to recover the current ``SConscript`` file name with a `Python lambda expression`_ as seen in the ``SConstruct``
modifications below. If the current workflow uses more than one ``SConscript`` file, the ``workflow_configuration`` list
should be updated to include all configuration files for the archive task.

Next, we define the actual archive task using the `SCons`_ Tar builder :cite:`scons-man`. The archive target is
constructed from a prefix including the current project name and version in the ``SConstruct`` file. Including the
version number will allow us to keep multiple archives simultaneously, provided the version number is incremented
between workflow executions and as the project changes. We append the current workflow name in the archive target for
projects that may contain many unique, independent workflows which can be archived separately. The archive task sources
are compiled from all previous workflow targets and the workflow configuration file(s). In principle, it may be
desirable to archive the workflow's source files, as well. However, if a version control system is used to build the
version number as in :ref:`tutorial_setuptools_scm_waves`, the source files may also be recoverable from the version
control state which is embedded in the version number.

Finally, we create a dedicated archive alias to match the workflow alias. Here we separate the aliases because workflows
with large output files may require significant time to archive. This may be undesirable during workflow construction
and troubleshooting. It is also typical for the archival task to be performed once at reporting time when the
post-processing plots have been finalized.

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_regression_testing_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_11_archival_SConstruct
      :language: Python
      :diff: tutorials_tutorial_10_regression_testing_SConstruct

Note that we retrieve the project configuration ``SConstruct`` file name and location with a `Python lambda expression`_
:cite:`python`. We do this to recover the absolute path to the current configuration file and because some projects may
choose to use a non-default filename for the project configuration file. In Python 3, you would normally use the
``__file__`` attribute; however, this attribute is not defined for `SCons`_ configuation files. Instead, we can recover
the configuration file name and absolute path with the same method used in :ref:`tutorial_geometry_waves` and
:ref:`tutorial_partition_mesh_waves` for the Abaqus Python 2 journal files. For consistency with the configuration file
path, we assume that the parent directory of the configuration file is the same as the project root directory.

The environment is also modified to provide non-default configuration options to the `SCons`_ Tar builder. Here, we
request the ``bzip2`` compression algorithm of the archive file and a commonly used file extension to match. You can
read more about tar archives in the `GNU tar`_ documentation :cite:`gnu-tar` and the `SCons`_ Tar builder in the `SCons
manpage`_ :cite:`scons-man`.

*************
Build Targets
*************

4. Build the archive target. Note that the usual workflow target does not include the archive task because it is not
   required until the project developer is ready to begin final reporting.

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials
   $ scons tutorial_11_archival_archive --jobs=4

************
Output Files
************

The output should look identical to :ref:`tutorial_regression_testing_waves` with the addition of a single ``*.tar.bz2``
file. You can inspect the contents of the archive as below.

.. code-block:: bash

   $ pwd
   /path/to/waves-tutorials
   $ find build -name "*.tar.bz2"
   build/tutorial_11_archival/WAVES-TUTORIAL-0.1.0-tutorial_11_archival.tar.bz2
   $ tar -tjf $(find build -name "*.tar.bz2") | grep -E "parameter_set0|SConstruct|^tutorial_11_archival"
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
   SConstruct
   tutorial_11_archival

**********************
Workflow Visualization
**********************

View the workflow directed graph by running the following command and opening the image in your preferred image viewer.
First, plot the workflow with all parameter sets.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves visualize tutorial_11_archival_archive --output-file tutorial_11_archival.png --width=50 --height=12 --exclude-list /usr/bin .stdout .jnl .env .prt .com .msg .dat .sta

The output should look similar to the figure below.

.. raw:: latex

    \begin{landscape}
        \vspace*{\fill}

.. figure:: tutorial_11_archival.png
   :align: center

.. raw:: latex

        \vspace*{\fill}
    \end{landscape}

Now plot the workflow with only the first set, ``set0``.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves visualize tutorial_11_archival_archive --output-file tutorial_11_archival_set0.png --width=50 --height=8 --exclude-list /usr/bin .stdout .jnl .env .prt .com .msg .dat .sta --exclude-regex "set[1-9]"

The output should look similar to the figure below.

.. raw:: latex

    \begin{landscape}
        \vspace*{\fill}

.. figure:: tutorial_11_archival_set0.png
   :align: center

.. raw:: latex

        \vspace*{\fill}
    \end{landscape}
