.. _tutorial_data_extraction_waves:

############################
Tutorial 08: Data Extraction
############################

Many post-processing activities require a non-proprietary serialization format to provide common access to a mix of
analysis libraries and tools. The :ref:`parameter_generator_api` of this project uses the `xarray dataset`_ and H5
files, so it will be convenient to extract data results to a similar H5 file using matching coordinates for the
N-dimensional data.

Abaqus provides a scripting interface and a proprietary, binary output database file containing the simulation results.
While this object and interface is good for scripting with the Abaqus kernel and CAE features, the Python interface is
limited to the Python 2.7 environment that is shipped with Abaqus. When post-processing requires more Python libraries
or other third party tools, it is common to extract a portion of the Abaqus results to an intermediate file. To reduce
duplicated effort in extracting Abaqus ODB files to a common format, the :ref:`odb_extract_cli` command line utility and
the associated :meth:`waves.scons_extensions.abaqus_extract` builder are provided to parse the output of ``abaqus odbreport``
into several `xarray dataset`_ objects in an H5 file.

Future releases of |PROJECT| may include extract utilities for other numeric solvers.

**********
References
**********

* |PROJECT| :ref:`waves_scons_api` API: :meth:`waves.scons_extensions.abaqus_extract`
* :ref:`odb_extract_cli` CLI
* `Xarray`_ :cite:`xarray`
* `h5py`_ :cite:`h5py`
* `The HDF5 Group command-line-tools`_ :cite:`hdf5group`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

.. include:: version_check_warning.txt

*******************
Directory Structure
*******************

.. include:: tutorial_directory_setup.txt

.. note::

    If you skipped any of the previous tutorials, run the following commands to create a copy of the necessary tutorial
    files.

    .. code-block:: bash

        $ pwd
        /home/roppenheimer/waves-tutorials
        $ waves fetch --overwrite --destination eabm_package tutorials/eabm_package/__init__.py
        WAVES fetch
        Destination directory: 'eabm_package'
        $ waves fetch --overwrite --destination eabm_package/abaqus 'tutorials/eabm_package/abaqus/*'
        WAVES fetch
        Destination directory: 'eabm_package/abaqus'
        $ waves fetch --overwrite --destination eabm_package/python 'tutorials/eabm_package/python/__init__.py' 'tutorials/eabm_package/python/rectangle_compression_nominal.py' 'tutorials/eabm_package/python/rectangle_compression_cartesian_product.py'
        WAVES fetch
        Destination directory: 'eabm_package/python'
        $ waves fetch tutorials/tutorial_07_cartesian_product_SConstruct && mv tutorial_07_cartesian_product_SConstruct SConstruct
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'

4. Download and copy the ``tutorial_07_cartesian_product`` file to a new file named ``tutorial_08_data_extraction``
   with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_07_cartesian_product && cp tutorial_07_cartesian_product tutorial_08_data_extraction
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

**********
SConscript
**********

A ``diff`` against the ``tutorial_07_cartesian_product`` file from :ref:`tutorial_cartesian_product_waves` is included
below to help identify the changes made in this tutorial.

.. admonition:: waves-tutorials/tutorial_08_data_extraction

   .. literalinclude:: tutorials_tutorial_08_data_extraction
      :language: Python
      :diff: tutorials_tutorial_07_cartesian_product

The only new code in this tutorial adds the :meth:`waves.scons_extensions.abaqus_extract` builder task. Note that this task
falls within the parameterization loop and will be executed once per parameter set. :ref:`odb_extract_cli` will output
two files: ``rectangle_compression_datasets.h5``, which contains h5py paths to the `Xarray`_ datasets, and
``rectangle_compression.h5``, which contains h5py native datasets for anything that :ref:`odb_extract_cli` doesn't
organize into `Xarray`_ datasets and a list of group paths pointing at `Xarray`_ datasets in
``rectangle_compression_datasets.h5``. The second file also contains external links to the datasets file, so h5py
can be used to access all group paths if necessary. :ref:`tutorial_post_processing_waves` will introduce an example for
accessing and organizing the results files and concatenating the parameter study information.

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_cartesian_product_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_08_data_extraction_SConstruct
      :language: Python
      :diff: tutorials_tutorial_07_cartesian_product_SConstruct

*************
Build Targets
*************

5. Build the new targets

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons tutorial_08_data_extraction --jobs=4
   <output truncated>

************
Output Files
************

6. View the output files. The output files should match those introduced in :ref:`tutorial_cartesian_product_waves`, with
   the addition of the :ref:`odb_extract_cli` output files.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ find build/tutorial_08_data_extraction/ -name "*.h5"
   build/tutorial_08_data_extraction/parameter_set2/rectangle_compression.h5
   build/tutorial_08_data_extraction/parameter_set2/rectangle_compression_datasets.h5
   build/tutorial_08_data_extraction/parameter_set1/rectangle_compression.h5
   build/tutorial_08_data_extraction/parameter_set1/rectangle_compression_datasets.h5
   build/tutorial_08_data_extraction/parameter_set3/rectangle_compression.h5
   build/tutorial_08_data_extraction/parameter_set3/rectangle_compression_datasets.h5
   build/tutorial_08_data_extraction/parameter_set0/rectangle_compression.h5
   build/tutorial_08_data_extraction/parameter_set0/rectangle_compression_datasets.h5

See the :ref:`odb_extract_cli` and :meth:`waves.scons_extensions.abaqus_extract` documentation for an overview of the H5
file structure. You will notice that there are two H5 files per parameter set. The data is organized into a root file,
e.g. ``rectangle_compression.h5``, that contains the overall file structure, some unsorted meta data, and an xarray
object with a list of H5 group paths containing Xarray datasets. The second file, ``rectangle_compression_datasets.h5``
contains the actual Xarray dataset objects.

You can explore the structure of each file with `The HDF5 Group command-line-tools`_ below (the ``grep`` command
excludes the large, unsorted data in the ``odb`` group path).

.. code-block::
   :caption: rectangle_compression.h5

   $ h5ls -r build/tutorial_08_data_extraction/parameter_set0/rectangle_compression.h5 | grep -v odb
   /                        Group
   /RECTANGLE               Group
   /RECTANGLE/FieldOutputs  Group
   /RECTANGLE/FieldOutputs/ALL_ELEMENTS External Link {/projects/kbrindley/w13repos/waves/waves/tutorials/build/tutorial_08_data_extraction/parameter_set0/rectangle_compression_datasets.h5//RECTANGLE/FieldOutputs/ALL_ELEMENTS}
   /RECTANGLE/FieldOutputs/ALL_NODES External Link {/projects/kbrindley/w13repos/waves/waves/tutorials/build/tutorial_08_data_extraction/parameter_set0/rectangle_compression_datasets.h5//RECTANGLE/FieldOutputs/ALL_NODES}
   /RECTANGLE/HistoryOutputs Group
   /RECTANGLE/HistoryOutputs/ALLNODES External Link {/projects/kbrindley/w13repos/waves/waves/tutorials/build/tutorial_08_data_extraction/parameter_set0/rectangle_compression_datasets.h5//RECTANGLE/HistoryOutputs/ALLNODES}
   /RECTANGLE/Mesh          External Link {/projects/kbrindley/w13repos/waves/waves/tutorials/build/tutorial_08_data_extraction/parameter_set0/rectangle_compression_datasets.h5//RECTANGLE/Mesh}
   /xarray                  Group
   /xarray/Dataset          Dataset {4}

.. code-block::
   :caption: rectangle_compression_datasets.h5

   $ h5ls -r waves/tutorials/build/tutorial_08_data_extraction/parameter_set0/rectangle_compression_datasets.h5
   /                        Group
   /RECTANGLE               Group
   /RECTANGLE/FieldOutputs  Group
   /RECTANGLE/FieldOutputs/ALL_ELEMENTS Group
   /RECTANGLE/FieldOutputs/ALL_ELEMENTS/E Dataset {1, 5, 1, 4, 4}
   /RECTANGLE/FieldOutputs/ALL_ELEMENTS/E\ values Dataset {4}
   /RECTANGLE/FieldOutputs/ALL_ELEMENTS/S Dataset {1, 5, 1, 4, 4}
   /RECTANGLE/FieldOutputs/ALL_ELEMENTS/S\ values Dataset {4}
   /RECTANGLE/FieldOutputs/ALL_ELEMENTS/elements Dataset {1}
   /RECTANGLE/FieldOutputs/ALL_ELEMENTS/integration\ point Dataset {4}
   /RECTANGLE/FieldOutputs/ALL_ELEMENTS/integrationPoint Dataset {1, 4}
   /RECTANGLE/FieldOutputs/ALL_ELEMENTS/step Dataset {1}
   /RECTANGLE/FieldOutputs/ALL_ELEMENTS/time Dataset {5}
   /RECTANGLE/FieldOutputs/ALL_NODES Group
   /RECTANGLE/FieldOutputs/ALL_NODES/U Dataset {1, 5, 4, 2}
   /RECTANGLE/FieldOutputs/ALL_NODES/U\ values Dataset {2}
   /RECTANGLE/FieldOutputs/ALL_NODES/nodes Dataset {4}
   /RECTANGLE/FieldOutputs/ALL_NODES/step Dataset {1}
   /RECTANGLE/FieldOutputs/ALL_NODES/time Dataset {5}
   /RECTANGLE/HistoryOutputs Group
   /RECTANGLE/HistoryOutputs/ALLNODES Group
   /RECTANGLE/HistoryOutputs/ALLNODES/U1 Dataset {1, 14}
   /RECTANGLE/HistoryOutputs/ALLNODES/U2 Dataset {1, 14}
   /RECTANGLE/HistoryOutputs/ALLNODES/node Dataset {1}
   /RECTANGLE/HistoryOutputs/ALLNODES/step Dataset {1}
   /RECTANGLE/HistoryOutputs/ALLNODES/time Dataset {14}
   /RECTANGLE/HistoryOutputs/ALLNODES/type Dataset {1}
   /RECTANGLE/Mesh          Group
   /RECTANGLE/Mesh/CPS4R    Dataset {1}
   /RECTANGLE/Mesh/CPS4R_mesh Dataset {1, 4}
   /RECTANGLE/Mesh/CPS4R_node Dataset {4}
   /RECTANGLE/Mesh/node     Dataset {4}
   /RECTANGLE/Mesh/node_location Dataset {4, 3}
   /RECTANGLE/Mesh/section_category Dataset {1}
   /RECTANGLE/Mesh/vector   Dataset {3}

Each group path directly above a ``Dataset`` entry can be opened with `Xarray`_, e.g.
``/RECTANGLE/FieldOutputs/ALL_ELEMENTS`` as

.. code-block::

   import xarray
   extracted_file = "build/tutorial_08_data_extraction/parameter_set0/rectangle_compression.h5"
   group_path = "/RECTANGLE/FieldOutputs/ALL_ELEMENTS"
   field_outputs = xarray.open_dataset(extracted_file, group=group_path)

The structure is separated this way to aid automated exploration of the data structure. The root file,
``rectangle_compression.h5`` may be opened with `h5py`_ to obtain the Xarray datasets list in the ``/xarray/Dataset``
group path. Then the datasets file ``rectangle_compression_datasets.h5`` file may be opened separately with `Xarray`_.

In practice when you know the Xarray dataset path(s) relevant to your workflow, you may also go directly to the datasets
file. :ref:`tutorial_post_processing_waves` will introduce post-processing with the :ref:`odb_extract_cli` and
:meth:`waves.scons_extensions.abaqus_extract` H5 files.

.. code-block::

   import xarray
   extracted_file = "build/tutorial_08_data_extraction/parameter_set0/rectangle_compression_datasets.h5"
   group_path = "/RECTANGLE/FieldOutputs/ALL_ELEMENTS"
   field_outputs = xarray.open_dataset(extracted_file, group=group_path)

**********************
Workflow Visualization
**********************

View the workflow directed graph by running the following command and opening the image in your preferred image viewer.
First, plot the workflow with all parameter sets.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves visualize tutorial_08_data_extraction --output-file tutorial_08_data_extraction.png --width=36 --height=12 --exclude-list /usr/bin .stdout .jnl .env .prt .com .msg .dat .sta

The output should look similar to the figure below.

.. raw:: latex

    \begin{landscape}
        \vspace*{\fill}

.. figure:: tutorial_08_data_extraction.png
   :align: center

.. raw:: latex

        \vspace*{\fill}
    \end{landscape}

Now plot the workflow with only the first set, ``set0``.

.. code-block::

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves visualize tutorial_08_data_extraction --output-file tutorial_08_data_extraction_set0.png --width=28 --height=6 --exclude-list /usr/bin .stdout .jnl .env .prt .com .msg .dat .sta --exclude-regex "set[1-9]"

The output should look similar to the figure below.

.. raw:: latex

    \begin{landscape}
        \vspace*{\fill}

.. figure:: tutorial_08_data_extraction_set0.png
   :align: center

.. raw:: latex

        \vspace*{\fill}
    \end{landscape}

This single set directed graph image should look very similar to the :ref:`tutorial_cartesian_product_waves` directed
graph. The data extraction step has added the ``*.h5`` files which take the proprietary ``*.odb`` data format and
provide ``h5py`` and ``xarray`` dataset files.
