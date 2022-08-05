.. _version_control:

***************
Version Control
***************

Software Carpentry: Git Novice - https://swcarpentry.github.io/git-novice/index.html :cite:`swc-git,SoftwareCarpentry`

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
system `git`_ :cite:`git`, which was released in 2005 :cite:`pro-git`.

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

* Display contributor information: commits, name, email. Differences in name for a single person are artifacts of
  providing different biographical information over project history. Typically this arises when working from more than
  one computer with slight differences in user account settings.

  .. code-block::

     $ git shortlog --summary --numbered --email
     794  Kyle Brindley <kbrindley@lanl.gov>
     134  Thomas Phillip Roberts <tproberts@lanl.gov>
      90  Prabhu Khalsa <pkhalsa@pn1934993.lanl.gov>
      84  Kyle Andrew Brindley <kbrindley@lanl.gov>
       6  Prabhu Singh Khalsa <prabhu@lanl.gov>
       2  Sergio Cordova <sergioc@lanl.gov>
       1  Sergio Rene Cordova <sergioc@lanl.gov>

* Display all commits that have affected the source file of the current section.

  .. code-block::

     $ git log -- docs/computational_practices_version_control.rst
     commit bdeac0a7940a1e366bd69a3fe5e81960f0322f00 (HEAD -> 123-theory-manual-version-control-section, origin/123-theory-manual-version-control-section)
     Author: Kyle Brindley <kbrindley@lanl.gov>
     Date:   Sat Jun 4 09:44:47 2022 -0600

         DOC: add git discussion to version control practices

     commit 8f6b997bba6a8d17222f0c788b5ff36ce8321e52
     Author: Kyle Brindley <kbrindley@lanl.gov>
     Date:   Sat Jun 4 08:47:51 2022 -0600

         DOC: draft importance of version control

     commit b569dc8537237c8521c280f183b81b532cfb1577
     Author: Kyle Brindley <kbrindley@lanl.gov>
     Date:   Fri Jun 3 14:49:41 2022 -0600

         MAINT: separate pages for the computational practices toc tree

* Show summary information for the most recent commits to the project's documentation.

  .. code-block::

     $ git log --oneline -n 10 -- docs
     bdeac0a (HEAD -> 123-theory-manual-version-control-section, origin/123-theory-manual-version-control-section) DOC: add git discussion to version control practices
     8f6b997 DOC: draft importance of version control
     07a30ee (origin/144-add-a-setup-page-to-the-user-manual, 144-add-a-setup-page-to-the-user-manual) MAINT: fix quickstart anchor
     eda85cd DOC: add quickstart time estimate
     4bc1acf DOC: starting point clarifications
     5621d50 DOC: startup options dicussion
     bdcd044 DOC: clarify time estimate format
     842920b DOC: draft guesses at tutorial time estimates
     be5e2e2 DOC: commit to hours and minutes
     3a093c3 DOC: adjust prereq typesetting

* Show detailed information about a commit, including the actual file changes

  .. code-block::

     $ git show 0a00f5704d9299ffd77c83100f90676f2f509456
     commit 0a00f5704d9299ffd77c83100f90676f2f509456
     Author: Prabhu Khalsa <pkhalsa@pn1934993.lanl.gov>
     Date:   Thu Jun 2 11:31:48 2022 -0600

         DOC: Adding cli documentation to rst docs

     diff --git a/docs/cli.rst b/docs/cli.rst
     index 114025a..cda1894 100644
     --- a/docs/cli.rst
     +++ b/docs/cli.rst
     @@ -50,3 +50,10 @@ ODB Extract

      .. argparse::
         :ref: waves.abaqus.odb_extract.get_parser
     +
     +*********
     +Sta Parse
     +*********
     +
     +.. argparse::
     +   :ref: waves.abaqus.sta_parse.get_parser
