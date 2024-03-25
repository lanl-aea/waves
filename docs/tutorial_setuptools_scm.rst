.. _tutorial_setuptools_scm:

########################
Tutorial: setuptools_scm
########################

.. include:: wip_warning.txt

For the reproducible version number, it is beneficial to use a versioning scheme that includes information from the
project's version control system, e.g. `git`_. The `WAVES`_ project uses `git`_ and `setuptools_scm`_
:cite:`setuptools_scm` to build version numbers with a clean version number that is uniquely tied to a single commit,
e.g. ``1.2.3``, or a version number appended with the short git hash to uniquely identify the project commit.

**********
References
**********

* `setuptools_scm`_ :cite:`setuptools_scm`

***********
Environment
***********

.. include:: tutorial_environment_activation.txt

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
        $ waves fetch --overwrite --tutorial 12 && mv tutorial_12_archival_SConstruct SConstruct
        WAVES fetch
        Destination directory: '/home/roppenheimer/waves-tutorials'

4. Download the ``tutorial_12_archival`` file with the :ref:`waves_cli` :ref:`waves_fetch_cli` subcommand. The
   ``SConscript`` file ``tutorial_12_archival`` does not need to change because we are already using the project
   configuration ``env["version"]`` in the archive file name.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ waves fetch --overwrite tutorials/tutorial_12_archival
   WAVES fetch
   Destination directory: '/home/roppenheimer/waves-tutorials'

****************************
setuptools_scm configuration
****************************

5. Create a file named ``pyproject.toml`` using the contents below.

.. admonition:: waves-tutorials/pyproject.toml

    .. literalinclude:: tutorials_pyproject.toml
        :lineno-match:

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_archival` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-tutorials/SConstruct

   .. literalinclude:: tutorials_tutorial_setuptools_scm_SConstruct
      :language: Python
      :diff: tutorials_tutorial_12_archival_SConstruct

**********************
Version control system
**********************

6. Initialize a git repository in the tutorial directory

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ git init

7. Put the current tutorial's files under version control

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ git add SConstruct pyproject.toml tutorial_12_archival
   $ git commit -m "Initial commit for git tag version numbers using setuptools_scm"
   <output truncated>

8. Create a git tag version number

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ git tag 0.1.0

9. Verify that setuptools_scm is correctly picking up the git tag for the version number

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ python -m setuptools_scm
   0.1.0

*************
Build Targets
*************

10. Build (or re-build) the archive target from :ref:`tutorial_archival`.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons tutorial_12_archival_archive --jobs=4
   <output truncated>

************
Output Files
************

The output should look identical to :ref:`tutorial_archival` with the exception that the archive ``*.tar.bz2``
file may contain version information relating to the git short commit hash. One side effect of the dynamic version
number is that the archive task will always re-run when changes are made to the project repository, including any
uncommitted changes to tracked files.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ find build -name "*.tar.bz2"
   build/tutorial_12_archival/WAVES-TUTORIAL-0.1.0.tar.bz2

To explore the dynamic version number, you can add new git commits. For instance, you might add a ``.gitignore`` file
from the contents below

.. admonition:: waves-tutorials/.gitignore

   .. literalinclude:: tutorials_gitignore
        :lineno-match:

11. Place the ``.gitignore`` file under version control

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ git add .gitignore
   $ git commit -m "MAINT: Ignore build artifacts"
   [main ad02fc7] MAINT: Ignore build artifacts
    1 file changed, 33 insertions(+)
    create mode 100644 .gitignore

12. Observe the dynamic version number change. The git short hash, ``ad02fc7``, will differ for every user and is
    specific to your git repository.

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ python -m setuptools_scm
   0.1.0.dev1+gad02fc7

.. note::

   The leading ``g`` before the short hash ``ad02fc7`` is not part of the hash. `setuptools_scm`_ can work with several
   version control systems and uses the leading ``g`` to indicate that this is a git repository.

13. Re-build the archive target and note the archive file name change to match the version number from the previous step

.. code-block:: bash

   $ pwd
   /home/roppenheimer/waves-tutorials
   $ scons tutorial_12_archival_archive --jobs=4
   <output truncated>
   $ find build -name "*.tar.bz2"
   build/tutorial_12_archival/WAVES-TUTORIAL-0.1.0.tar.bz2
   build/tutorial_12_archival/WAVES-TUTORIAL-0.1.0.dev1+gad02fc7.tar.bz2
