.. only:: epub

   .. include:: epub_copyright.txt

#########
|project|
#########

.. include:: project_brief.txt

.. raw:: latex

   \part{Computational Practices}

.. _computational_tools:

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Computational Practices

   computational_practices_introduction
   computational_practices_version_control
   computational_practices_documentation
   computational_practices_build_system
   computational_practices_compute_environment
   computational_practices_regression_testing
   computational_practices_archival

.. raw:: latex

   \part{User Manual}

.. _user_manual:

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: User Manual

   abstract
   installation
   tutorial_quickstart
   tutorial_introduction
   tutorial_core
   tutorial_supplemental
   tutorial_wip
   templates
   api
   cli

.. raw:: latex

   \part{Help and Reference}

.. toctree::
   :hidden:
   :caption: Help and Reference
   :maxdepth: 1

   license
   citation
   internal_api
   devops
   release_philosophy
   changelog
   zreferences
   glossary

.. raw:: latex

   \part{Appendices}

.. toctree::
   :hidden:
   :caption: Appendices
   :maxdepth: 1

   tutorial_api
   tutorial_cli

.. raw:: latex

   \part{Indices and Tables}

.. only:: html

   .. |github-pages| image:: https://img.shields.io/github/actions/workflow/status/lanl-aea/waves/pages.yml?branch=main&label=GitHub-Pages
      :target: https://lanl-aea.github.io/waves/

   .. |github-release| image:: https://img.shields.io/github/v/release/lanl-aea/waves?label=GitHub-Release
      :target: https://github.com/lanl-aea/waves/releases

   .. |conda-forge version| image:: https://img.shields.io/conda/vn/conda-forge/waves
      :target: https://anaconda.org/conda-forge/waves

   .. |conda-forge downloads| image:: https://img.shields.io/conda/dn/conda-forge/waves.svg?label=Conda%20downloads
      :target: https://anaconda.org/conda-forge/waves

   .. |pypi version| image:: https://img.shields.io/pypi/v/waves-workflows?label=PyPI%20package
      :target: https://pypi.org/project/waves-workflows/

   .. |pypi downloads| image:: https://img.shields.io/pypi/dm/waves-workflows?label=PyPI%20downloads
      :target: https://pypi.org/project/waves-workflows/

   .. |zenodo| image:: https://zenodo.org/badge/591388602.svg
      :target: https://zenodo.org/badge/latestdoi/591388602

   |github-pages| |github-release| |conda-forge version| |conda-forge downloads| |pypi version| |pypi downloads| |zenodo|

   |

   .. grid:: 1 2 2 2
      :gutter: 2
      :margin: 2

      .. grid-item-card:: :octicon:`book` Computational Practices
         :link: practices_introduction
         :link-type: ref

         Computional science and engineering practices primer with a recommended practical curriculum

      .. grid-item-card:: :octicon:`light-bulb` Why |PROJECT|?
         :link: abstract
         :link-type: ref

         Four paragraph motivation for build systems and |PROJECT| in computational science and engineering

      .. grid-item-card:: :octicon:`download` Installation
         :link: installation
         :link-type: ref

         Installation with conda-forge or PyPI

      .. grid-item-card:: :octicon:`rocket` Quickstart
         :link: tutorial_quickstart
         :link-type: ref

         Minimal working examples of build system integration with parameter studies

      .. grid-item-card:: :octicon:`mortar-board` Tutorials
         :link: tutorial_introduction
         :link-type: ref

         Introduction to the full tutorial suite

      .. grid-item-card:: :octicon:`repo-template` Modsim Templates
         :link: modsim_templates
         :link-type: ref

         Start from a modsim template project

      .. grid-item-card:: :octicon:`code-square` API
         :link: external_api
         :link-type: ref

         Public application program interface (API)

      .. grid-item-card:: :octicon:`command-palette` CLI
         :link: cli
         :link-type: ref

         Public command line interface (CLI)
