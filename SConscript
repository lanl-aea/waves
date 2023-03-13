#! /usr/bin/env python

import pathlib

# Inherit the parent construction environment
Import('source_dir')

copy_files = (
    (f"{source_dir}/README.txt", "README.rst"),
    (f"{source_dir}/CITATION.bib", "CITATION.bib"),
    (f"{source_dir}/LICENSE.txt", "LICENSE.txt"),
    (f"{source_dir}/environment.txt", "environment.txt")
)

for target, source in copy_files:
    target = str(pathlib.Path(target))
    Command(target=target,
            source=source,
            action=Copy("$TARGET", "$SOURCE"))
