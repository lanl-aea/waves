.. _data_archival:

*************
Data Archival
*************

The :ref:`version_control` section introduced the idea of using version control software from the software engineering
community to mange model and simulation source files and post-processing scripts. For any portions of a computational
engineering workflow that must be parameterized or can be stored as text, the VCS features for change history,
collaboration, and conflict resolution are powerful tools. However, except in the case of files used in the
documentation, it is not generally appropropriate to put the output artifacts of workflow under version control. The
workflow output artifacts are frequently large, as in the case of simulation output, or binary files, as in the case of
images for visualization. Some of these files will make it into reporting requirements, and are therefore appropriate to
version control as a documentation or report source file. Due to the computational cost in producing simulation data,
the remainder may be valuable for archival in a dedicated database.
