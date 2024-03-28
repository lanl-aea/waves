.. _documentation:

*************
Documentation
*************

.. note:: Related curriculum

   `Sphinx`_ tutorial: https://www.sphinx-doc.org/en/master/tutorial/index.html :cite:`sphinx,sphinx-tutorial`

Traditionally, most engineering simulation and analysis projects publish a technical report as the final deliverable.
Some projects may go further and deliver archives or databases of simulation input and output files. These documentation
and archival deliverables may be sufficient for short projects, simple simulation workflows, or when there are a small
number of contributors. When a project grows in complexity, contributors, or lifespan, a more complete project
documentation strategy is required. Engineering analysis projects and their associated :term:`modsim repository` can have
similar complexity to a large software project, and many of the same documentation sections are required:

* User manual
* Theory manual
* Application program interface (:term:`API`)
* Command-line interface (:term:`CLI`)
* Developer manual
* Release philosophy
* Strategic plan/feature schedule
* Changelog

Of course, no documentation for an analysis project would be complete without a discussion of the engineering analysis
reports as well.

* Analysis reports

The documentation should include everything required for new developers to begin contributing to the project, as well as
the necessary elements of a technical report. The user manual should explain what simulations are available, what
purpose they serve, and how to run them. A theory manual should discuss any relevant analytical solutions, what
numerical solutions were chosen and why, and any critical assumptions. The application program interface (API) and
command-line interface (CLI) should document the interfaces, behavior, and usage of all project-specific scripts and
executables in sufficient detail that a new project team member can understand and use what is available without
examining the project source code. A developer manual will detail the contribution guidelines, style guides, version
control behavior, continuous integration and automation solutions, and testing requirements of the project. The release
philosophy should indicate how and when new reports are released and when the project version number changes. A feature
or planning schedule can document what new simulation features are desirable and when they might be implemented to keep
analysis stakeholders informed about project progress and priorities. Finally, the changelog provides a summary of the
project history.

While most of these documentation sections will not make it into technical reports, many elements of the documentation
may overlap with the technical report. If the technical reports are compiled from a markup or markdown language, such
as `Markdown`_ :cite:`markdown`, `LaTeX`_ :cite:`latex`, or `reStructuredText`_ :cite:`rst`, then the source content may
be shared by both the documentation and the report. This is valuable to avoid duplicate content that may become out of
sync and to reduce long-term maintenance overhead.

The practical examples in the :ref:`user_manual` use `reStructuredText`_ compiled with `Sphinx`_ :cite:`sphinx`, which
integrates markup documentation with automated generation of API and CLI documentation from Python docstrings. An
example of modsim documentation is included as part of the `MODSIM-TEMPLATE`_ and is webhosted in the `MODSIM-TEMPLATE
documentation`_.
