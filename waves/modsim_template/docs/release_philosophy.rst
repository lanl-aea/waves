.. _releasephilosophy:

##################
Release Philosophy
##################

This section discusses topics related to |project| releases and version numbering.

***************
Version Numbers
***************

The |project| project follows the `PEP-440`_ standard for version numbering. The
production release version number uses the three component ("major.minor.micro")
scheme. The developement version number follows the production
release number with an appended ".dev" local version number. The version numbers
correspond to git tags in the `upstream repository`_ which point to a static
release of the |project| project.

Because the deployed release of the developer version is constantly updated
against development work, the version number found in the developer version
contains additional information. During deployment, the developer version number
is appended with the git information from the most recent build. This
information contains the most recent git tag ("major.minor.micro.dev") followed
by the number of commits since the last production release and a short hash.

Major Number
============

The major number is expected to increment infrequently. After the first major release, it is recommended that the major
version number only increments for major breaking changes.

Minor Number
============

The minor number is updated for the following reasons:

* New features
* Major internal implementation changes
* Non-breaking interface updates

Incrementing the minor version requires a manual update to the release number found in the Git tags on a
dedicated release commit. Until the first major release, minor version changes may also contain breaking changes. It is
recommended that all minor version changes are announced to the user community prior to release.

Micro Number
============

The micro version number indicates the following changes:

* Bug fixes
* Minor internal implementation changes

Until the first major release, micro version number releases may be made without announcement at the discretion of the
lead developer. It is recommended that the developer community periodically discuss priorities for minor version release
with the user community.

.. _releasebranchreq:

***************************
Release Branch Requirements
***************************

All version requires a manual update to the release number on a dedicated release commit. Versions are built from Git
tags for the otherwise automated `setuptools_scm`_ version number tool. Tags may be added directly to a commit on the
``main`` branch, but a release branch is encouraged.

Steps needed for a release include:

1. Create a release branch, e.g. ``release-0-4-1``.
2. Modify ``docs/changelog.rst`` to move version number for release MR commit and add description as relevant.
3. Check and update the ``CITATION.bib``, ``CITATION.cff``, and ``waves/modsim_template/docs/references.bib`` file to
   use the new version number and release date.
4. Commit changes and submit a merge request to the ``main`` branch at the `upstream repository`_.
5. Solicit feedback and make any required changes.
6. Immediately prior to merge, add the new version tag to the most recent commit.

   .. code-block::

      $ git tag 0.4.1
      $ git push origin release-0-4-1 --tags

7. Merge the release branch to ``main``
8. Create a new release for the new tag: https://re-git.lanl.gov/aea/python-projects/waves/-/releases
