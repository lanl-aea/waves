.. _compute_environment:

*******************
Compute Environment
*******************

.. note:: Related Curriculum

   Conda environments: https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html
   :cite:`conda,conda-gettingstarted`

Compute environment management is critical to any project that executes on more than one server or computer. This is
true of most projects, where local development is performed on a local desktop or laptop, but the simulations must be
executed on a remote server or computer cluster with high performance computing (HPC). Because modsim developers may not
have administrative or root permissions on the remote servers where their simulations are executed, virtual environments
are used to provide consistency between servers. Some types of virtual environments may also provide cross-platform
environment consistency.

There are two major components relevant to the compute environment discussion for modsim workflows: the installed
software and the operating system (OS) search ``PATH``. Most modsim developers will be familiar with installing software
on their local computer. When running a simulation workflow from a command-line shell, the system ``PATH`` variable
tells the shell how to find executable software. System paths may be modified by user configuration files; however,
managing and maintaining a common set of configuration files among several servers and multiple collaborators can be a
difficult and error-prone task, often resulting in the common "But it works on *my* computer" complaint.

Instead of managing an ever-growing ``case`` or ``if`` structure to handle system changes out of your control, one
solution to managing a common environment is to keep a version-controlled environment file used for creating a common
virtual compute environment. Virtual environments will handle ``PATH`` manipulation, and many come with associated
package managers that can install software to a common location managed by the virtual environment. The software
installed by the package manager is then accessed by activation of the virtual environment, which handles the OS and
system specific ``PATH`` changes for you. This pushes the difficulties of managing a common project environment into the
realm of version control, where developers now only need to rebuild their virtual environment when the
version-controlled environment file changes. When combined with continuous integration, any commonly used servers can
have the shared environment updated automatically on changes to the environment file.

In the `WAVES`_ project, a minimal `Conda`_ environment file is maintained under version control and used for
:ref:`testing`, shared compute environment management, and packaging with a continuous integration server for automatic
testing and deployment on every change to the project source code. A similar `MODSIM-TEMPLATE environment file`_ is
included in the tutorials as a starting point for :term:`modsim repository` environment management. The `Anaconda
documentation`_ includes good tutorials and references for `Conda environment management`_. `Conda`_ was chosen as the
package manager and virtual environment tool due to the popularity of Python as a scripting language and the
Python-centric nature of the scripting APIs for many engineering-analysis software tools.

While `Conda`_ is known primarily for Python package management, it is a general package manager and can package,
deploy, and manage packages of many different programming languages and mixed language packages. This makes it an
excellent tool for supporting Fortran, C, or C++ subroutines that most engineering analysis software allows to extend
the software's built-in behavior. As an engineering project grows and collaborates with material modeling and other
research projects, it may be beneficial to package supporting libraries and packages for `conda-forge`_ or even a
self-hosted `custom conda channel`_.

There are several engineering numeric solvers developed by the open-source community, and some are even distributed by
package managers, including `Conda`_. However, most commercial engineering analysis software is not packaged for a
package manager and instead provides licenced installation media. In this case, it may be difficult to include the
commercial software in a virtual environment.

Most :ref:`build_system` software offer solutions to executable path management separately from the activated virtual
environment and allow mixed use of software discovered on ``PATH`` and specified by absolute path. In the `SCons`_
build system, users are encouraged to explicitly specify software without relying on ``PATH`` to avoid ambiguous
system-configuration requirements. Another benefit of the explicit `SCons construction environment`_ is the ability to
define tasks with mutually incompatible execution environments. For instance, if one portion of the workflow requires a
numeric solver with dependencies that are incompatible with the post-processing task, `SCons`_ can configure both tasks
with a unique construction environment :cite:`scons-user`. This allows the project to maintain a single, uninterrupted
workflow, despite the conflicting software requirements. This approach is demonstrated in several |PROJECT|
:ref:`supplemental_lessons` using the :meth:`waves.scons_extensions.shell_environment` function.

A more generalized solution has been adopted by high performance computing, which often requires the system
administrators to provide multiple, conflicting versions of software side by side. `Environment modules`_ and the
``module`` software help users manage a project-specific environment on a multi-user compute server. For collaborative
efforts and version-controlled consistency, system ``PATH`` management with a project-specific module file can help tie
together system resources and a virtual environment in a common way for all contributors.

There is also an HPC focused package manager, `Spack`_, which can create targeted software installations optimized for
your system :cite:`spack`. `Spack`_ supports Linux and macOS, so it can be used for workflow development on local
machines before simulations are executed on HPCs. Like `Conda`_, `Spack`_ supports user environment installation so
project environments can be created on systems where the project and users do not have administration privileges.

`WAVES`_ is deployed on `conda-forge`_, `PyPI`, and `Spack`_ to provide users with more flexible choices in compute
environment management tools.
