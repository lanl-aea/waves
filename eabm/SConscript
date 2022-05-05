#! /usr/bin/env python
#
# Inherit the parent construction environment
Import('documentation_source_dir')

# TODO: find a more robust method to link to the README.txt target without assuming relative paths
Command(target=f"{documentation_source_dir}/README.txt",
        source="README.rst",
        action=Copy("$TARGET", "$SOURCE"))
