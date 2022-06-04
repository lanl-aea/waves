.. _version_control:

***************
Version Control
***************

Software Carpentry: Git Novice - https://swcarpentry.github.io/git-novice/index.html

As mentioned in the :ref:`practices_introduction`, version control software fills the role of a laboratory notebook for
computational engineering. Keeping a laboratory notebook is a fundamental practice of experimental engineering and
science disciplines. They keep a record of who did what, when and how they did it, and why. Sometimes, they may even be
the original data records from experimental observations. Laboratory notebooks with bound pages and recorded in ink also
provide legal protections against fraud and to establish intellectual property (IP) precedence.

While there are software available that provide electronic laboratory notebooks, for computational practice version
control software provides a similar record of who, what, when, how, and why. Additionally, version control software
provides the usual benefits of version control such as the ability to uniquely reproduce the state of previous work and
the ability to manage and resolve content conflicts from contributors working in parallel.

Version control software is also referred to as revision control, source control, or source code management. There have
been a variety of popular version control software dating back to the early 1970s. Today, there are many version control
software to choose from, with a range of implmente concepts. This section will focus on the distributed version control
system `git`_, which was released in 2005 :cite:`pro-git`.

Git tracks changes to collections of files in a project. The user creates incremental "commits" which form a directed
graph of project history, called "branches". As the commits are created and added to history, the use can supply a
commit message to describe the changes. Good messages answer questions about the purpose and design intent about the
changes; the "why" of a laboratory notebook. Included with the commit is meta data identifying the commit author, "who",
the files and the granular changes themselves, "what", and a timestamp, "when". The commit is assigned a unique
identifier called the commit "hash".

When users limit commits to small units of work and write quality messages describing the purpose of the changes, the
Git history log provides both a method to recover previous project states and a record for the 'who', 'what', 'when' and
'why' of project progression. Beyond reading the log as a linear chronological history of project development, the Git
log can also be filtered to directly answer these questions about specific content in the project. For instance, Git
tracks the association between specific lines in a text file and the commit hash and message that most recently edited
that line, so questions about the purpose of a specific portion of a file may be recovered quickly. With more advanced
filtering, the Git log can display all commit entries that touched a specific file, set of files, edits by a specific
author, etc.

There is an abundance of documentation, tutorials, and recommended practices in the use of `git`_ and other version
control software systems and practices. Instead of re-creating a tutorial here, this section will end with a few
examples of a Git log from the current project.


