************
Introduction
************

This manual will attempt to motivate the use of an `automated build system`_ for the purposes of computational science
and engineering. As part of this motivation, the surrounding computational practices of version control, documentation,
compute environment management, regression testing, and continuous integration will also be addressed as applied to the
practice of computational engineering. Specifically, this manual intends to motivate the adoption of these traditional
software engineering practices for use in research and production engineering simulation projects.

This manual is not the first such effort in the greater scientific computing community. In fact, the authors relied
heavily on the lesson plans of the `Software Carpentry`_, established to teach computing skills to researchers in 1998
:cite:`SoftwareCarpentry`. As the intention for this manual is to lay out fundamental practices of engineering
computing, it will not attempt to fully teach the underlying concepts and will instead reference the well designed lesson
plans of the `Software Carpentry`_.

Where possible, this manual will explain to general computing practices and concepts and limit discussion of specific
software implementations to examples or vehicles for practice in concrete application. The specific software taught by
the `Software Carpentry`_ curriculum is an excellent starting point to learn the core concepts of computational
engineering. However, the authors have found that applications to engineering simulation and analysis require
translation of these software development concepts into the language and workflows of computational engineers. Adopting
these computational tools may require engineers to re-imagine their workflows in some combination of traditional
engineering and software concepts.

It has also been necessary to extend existing software build systems for engineering practices beyond the simple
wrapping of engineering software execution. Where necessary, examples of specific software and their method of extension
to engineering simulations will be given, with reference to the :ref:`user_manual` for recommended practical use. Where
this manual relies on specific implementation examples, it should be understood that the practicing engineer may find
that different software is more amenable to their specific work. It is always the overall collection of computational
practices is more important than any specific software implementation. The ability to recognize which concepts are
implemented by a software package will make a practicing engineer agile to changing project needs, computing resources,
numeric solvers, programming languages, and even available funding.

Core Concepts
-------------

The core concepts of computational engineering practice are listed below in the rough order of project maturity. That
is, those things listed near the beginning of the list should be implemented early in the life-cycle of all projects,
regardless of expected project growth, re-use, or impact. Particularly, version control should be implemented at the
very beginning of a computational project, even with the earliest project brainstorming session. As the foundational
practice of computational engineering, version control fills the role of a laboratory notebook and the strict practice
of detailed and regular entries are equally important.

* :ref:`version_control`
* :ref:`documentation`
* :ref:`build_system`
* :ref:`compute_environment`
* :ref:`testing`
* :ref:`continuous_integration`

Those practices at the end of the list are more costly to implement and therefore more valuable for mature or long-lived
projects. However, an engineer familiar with the computational tools implementing these practices will find that even
small, short-term projects benefit from implementing all of these concepts. In production engineering environments, it
is beneficial to implement the full range of computational engineering concepts in a "stub" repository as a starting
template for every project.

Recommended Practical Curriculum
--------------------------------

Beyond the reading in this document, the following is a recommended curriculum to learn a practical implementation of
these practices. It should be supplemented with lessons in the numeric solvers used in your engineering organization.
For the practical implementation found in the `WAVES`_ :ref:`user_manual`, the shell, Git, Python, and GNU Make
tutorials are considered prerequisites.

#. Software Carpentry: Shell Novice: http://swcarpentry.github.io/shell-novice/
#. Software Carpentry: Git Novice - https://swcarpentry.github.io/git-novice/index.html
#. Software Carpentry: Python Novice - https://swcarpentry.github.io/python-novice-inflammation/
#. Software Carpentry: GNU Make - https://swcarpentry.github.io/make-novice/
#. Conda environments: https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html
#. Sphinx tutorial: https://www.sphinx-doc.org/en/master/tutorial/index.html
#. Software Carpentry: Regular Expressions - https://librarycarpentry.org/lc-data-intro/index.html
