.. _data_archival:

*************
Data Archival
*************

The :ref:`version_control` section introduced the idea of using version control software (VCS) from the software
engineering community to mange model and simulation source files and post-processing scripts. For any portions of a
computational engineering workflow that must be parameterized or can be stored as text, the VCS features for change
history, collaboration, and conflict resolution are powerful tools. However, except in the case of files used in the
documentation, it is generally inappropropriate to put the output artifacts of the workflow under version control. The
VCS and :ref:`build_system` together preserve the source files and workflow to produce those output artifacts. Instead,
output artifacts should be archived in a suitable database.

Most organizations will already have policies related to data management, access, and archival. At the very least,
computational engineers and scientists will be familiar with project reporting. Those reports are archived in a library
or report database with metadata about their purpose and scope for review by peers and for the purposes of documenting
program decisions.

Historically, the report is considered to be sufficient for archival purposes if there is enough detail to allow another
researcher or engineer to recreate the original work from scratch. However, the scientific and academic communities are
moving towards stricter requirements for publishing data and methods
:cite:`nature-reporting-standards,science-editorial-policies`. Most journals have some policy related to public
publication of data, methods, and code necessary to interpret the study results and conclusions.

In the context of engineering organizations and businesses, the open-source or public accessibility standards may not
apply, but the internal data storage, accessibility, and security requirements may be stricter in practice. A
business may have invested significant effort in producing both the source files and simulation outputs. Starting a project
from scratch may waste significant staff time when relatively small investements in version control, build automation,
and data archival could allow reuse and identical reproduction of past effort. In safety-based applications, all files
related to the final reporting and decision making may be required for future audits by internal policy and legal
statute.

Regardless of motive, the workflow output artifacts are frequently large, as in the case of simulation output, or binary
files, as in the case of images for visualization. Some of these files will make it into reporting requirements and are
therefore appropriate to version control as a documentation or report source file. Of the remainder, some files will be
intermediate files used in the simulation processing or troubleshooting and can be safely discarded, with care to
preserve appropriate run-time metadata files required for reproducibility and traceability of the workflow.

The simulation results themselves may be quite valuable due to the computational cost of producing or processing them.
Outside the computational cost, these results may contain information relevant to calculations that are not performed in
the current work but may support answers to future questions. When considering data archival scope, the cost of storage
should be weighed against the cost of reproducing the same results. Computational workflows frequently produce very
large files on disk, which may prohibit archiving active data that is subject to change as the project refines the
simulation and analysis. In this case, it may be desirable to postpone data-archival activities until final reporting,
when the datasets supporting the report should be made read-only and preserved.
