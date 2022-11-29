.. _tutorial_setuptools_scm_waves:

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

The ``SConscript`` file ``tutorial_11_archival`` does not need to change because we are already using the project
configuration ``env["version"]`` in the archive file name.

****************************
setuptools_scm configuration
****************************

3. Create a file named ``pyproject.toml`` using the contents below.

.. admonition:: waves-eabm-tutorial/pyproject.toml

    .. literalinclude:: tutorials_pyproject.toml
        :lineno-match:

**********
SConstruct
**********

A ``diff`` against the ``SConstruct`` file from :ref:`tutorial_archival_waves` is included below to help identify the
changes made in this tutorial.

.. admonition:: waves-eabm-tutorial/SConstruct

   .. literalinclude:: tutorials_tutorial_setuptools_scm_SConstruct
      :language: Python
      :diff: tutorials_tutorial_11_archival_SConstruct

**********************
Version control system
**********************

4. Initialize a git repository in the tutorial directory

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ git init

5. Put the current tutorial's files under version control

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ git add SConstruct pyproject.toml tutorial_11_archival
   $ git commit -m "Initial commit for git tag version numbers using setuptools_scm"
   <output truncated>

6. Create a git tag version number

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ git tag 0.1.0

7. Verify that setuptools_scm is correctly picking up the git tag for the version number

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ python -m setuptools_scm
   0.1.0

*************
Build Targets
*************

8. Build (or re-build) the archive target from :ref:`tutorial_archival_waves`.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_11_archival_archive --jobs=4
   <output truncated>

************
Output Files
************

The output should look identical to :ref:`tutorial_archival_waves` with the exception that the archive ``*.tar.bz2``
file may contain version information relating to the git short commit hash. One side effect of the dynamic version
number is that the archive task will always re-run when changes are made to the project repository, including any
uncommitted changes to tracked files.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ find build -name "*.tar.bz2"
   build/tutorial_11_archival/WAVES-EABM-TUTORIAL-0.1.0.tar.bz2

To explore the dynamic version number, you can add new git commits. For instance, you might add a ``.gitignore`` file
from the contents below

.. admonition:: waves-eabm-tutorial/.gitignore

   .. literalinclude:: tutorials_gitignore
        :lineno-match:

9. Place the ``.gitignore`` file under version control

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ git add .gitignore
   $ git commit -m "MAINT: Ignore build artifacts"
   [main ad02fc7] MAINT: Ignore build artifacts
    1 file changed, 33 insertions(+)
    create mode 100644 .gitignore

10. Observe the dynamic version number change. The git short hash, ``ad02fc7``, will differ for every user and is
    specific to your git repository.

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ python -m setuptools_scm
   0.1.0.dev1+gad02fc7

.. note::

   The leading ``g`` before the short hash ``ad02fc7`` is not part of the hash. `setuptools_scm`_ can work with several
   version control systems and uses the leading ``g`` to indicate that this is a git repository.

11. Re-build the archive target and note the archive file name change to match the version number from the previous step

.. code-block:: bash

   $ pwd
   /path/to/waves-eabm-tutorial
   $ scons tutorial_11_archival_archive --jobs=4
   <output truncated>
   $ find build -name "*.tar.bz2"
   build/tutorial_11_archival/WAVES-EABM-TUTORIAL-0.1.0.tar.bz2
   build/tutorial_11_archival/WAVES-EABM-TUTORIAL-0.1.0.dev1+gad02fc7.tar.bz2
