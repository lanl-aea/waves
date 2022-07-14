.. _compute_environment:

*******************
Compute Environment
*******************

Conda environments: https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html

Compute environment management is critical to any project that executes on more than one server or computer. This is
true of most projects, where local development is performed on a local desktop or laptop, but the simulations must be
executed on a high performance computer (HPC). Because modsim developers may not have administrative or root permissions
on the remote servers where their simulations are executed, virtal environments are used to provide consistency between
servers. Some types of virtual environments may also provide some amount of cross-platform environment consistency.

There are two major components relevant to the compute environment discussion for modsim workflows: the installed
software and the operating system search ``PATH``. Most modsim developers will be familiar with installing software on
their local computer. When running a simulation workflow from a command line shell, the system ``PATH`` variable tells
the shell how to find executable software. System paths may be modified by user configuration files; however, managing
and maintaining a common set of configuration files among several servers and multiple collaborators can be a difficult
and error prone task, often resulting in the command "but it works on *my* computer" complaint.

Instead of managin an ever growing ``case`` or ``if`` structure to handle system changes out of your control, one
solution to managing a common environment is to keep a version controlled environment file used for creating a common
virtual compute environment. Virtual environments will handle ``PATH`` manipulation and many come with associated
package managers that can install software to a common location managed by the virtual environment. The software
installed by the package manager is then accessed by activation of the virtual environment, which handles the OS and
system specific ``PATH`` changes for you. This pushes the difficulties of managing a common project environment into the
realm of version control, where developers now only need to re-build their virtual environment when the version
controlled environment file changes. When combined with continuous integration, any commonly used servers can have the
shared environment updated automatically on changes to the environment file.

In the `WAVES`_ project, a minimal `Conda`_ environment is maintained under version control and used for :ref:`testing`,
shared compute environment management, and packaging all with a continuous integration server for automatic testing and
deployment with every change to the project source code. The `Anaconda documentation`_ includes good tutorials and
references for `Conda environment management`_. `Conda`_ was chosen as the package manager and virtual environment tool
do to the popularity of Python as a scripting language and the Python-centric nature of many engineering analysis
software tools.

While `Conda`_ is known primarily for Python package management, it is a general package manager and can package,
deploy, and manage packages of many different programming languages and even mixed language packages. This makes it an
excellent tool for developing supporting Fortran, C, or C++ subroutines that most engineering analysis software allows
to extend behavior. As an engineering project grows and collaborates with material modeling and other research projects,
it may be beneficial to package supporting libraries and packages for `conda-forge`_ or even a self-hosted `custom conda
channel`_.

There are several engineering numeric solvers developed by the open-source community and some are even packaged for
`Conda`_ or other package managers and virtual environments. However, most commercial engineering analysis software is
not packaged for a package manager and instead provides licenced installation media. In this case, it may be difficult
to include the commercial software in a virtual environment.

.. TODO: mention modulefiles and conda recipe wrappers.
