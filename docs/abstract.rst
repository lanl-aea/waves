.. _abstract:

##############
Why |PROJECT|?
##############

Managing digital data and workflows in modern computational science and engineering is a difficult and error-prone task.
The large number of steps in the workflow and complex web of interactions between data files results in non-intuitive
dependencies that are difficult to manage by hand. This complexity grows substantially when the workflow includes
parameter studies.

The software engineering community has solved this problem of dependency and interaction management with build system
software. Build systems are software that read task definitions and automatically construct the interaction diagram.
Instead of mapping the entire project workflow diagram manually, software developers can define small, individual tasks
of work that are easy to hold in their head and the build system constructs the full diagram of task interactions. After
constructing the workflow diagram, build systems manage the execution and re-execution of workflow tasks with minimal
intervention from the user. This reduces manual errors from incomplete workflow execution by ensuring all dependencies
are executed on an as-needed basis.

Despite the strong benefits of build systems, they have not been widely adopted in the computational engineering
community. Among other reasons, the build systems of the software engineering community are not suited to engineering
parametric studies. This is the primary hurdle to adoption. A secondary hurdle is that software build systems specialize
in compiling software and are neither documented for, nor support, engineering simulation software out-of-the-box.

|PROJECT| makes it possible to manage parameter study execution with traditional software build systems and provides
engineering simulation software support and documentation. This enables strong build automation in computational
engineering workflows. In practice, the use of build systems has demonstrated a reduction in time spent trouble-shooting
the workflow itself and faster turn-around in running and updating simulation results. Additionally, strongly enforced
build state and automated execution are two necessary requirements for engineering simulation verification (did we
correctly do what we said we did), reproducibility (can someone else produce the same results), and reduced staff spin
up time (how long until a new staff member can contribute meaningfully to a project).

You can read a more thorough discussion about build systems in the :ref:`computational_tools` :ref:`build_system`
discussion.
