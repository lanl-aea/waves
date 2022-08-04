import pathlib

# Set some semi-private project meta variables for package internal use to avoid hardcode duplication
_project_root_abspath = pathlib.Path(__file__).parent.resolve()
_project_name_short = _project_root_abspath.name.upper() 
_project_name = f"{_project_name_short} Analysis for Verified Engineering Simulations"
_project_bin_dir = _project_root_abspath / "bin" 
_abaqus_environment_file = "abaqus_v6.env"
_abaqus_environment_extension = f".{_abaqus_environment_file}"
_abaqus_solver_common_suffixes = [".odb", ".dat", ".msg", ".com", ".prt"]
_scons_substfile_suffix = ".in"
_stdout_extension = ".stdout"
# When built with ``noarch: python`` in recipe/meta.yaml, WAVES installs to:
#   $CONDA_PREFIX/lib/python3.8/site-packages/WAVES-*-py3.?.egg
# but documentation installs at
#   $CONDA_PREFIX/lib/python3.8/site-packages/waves/docs
_docs_directory = _project_root_abspath.parent.parent / 'waves/docs'
