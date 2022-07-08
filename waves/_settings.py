import pathlib

# Set some semi-private project meta variables for package internal use to avoid hardcode duplication
_project_root_abspath = pathlib.Path(__file__).parent.resolve()
_project_name_short = _project_root_abspath.name.upper() 
_project_name = f"{_project_name_short} Analysis for Validated Engineering Simulations"
_project_bin_dir = _project_root_abspath / 'bin' 
_abaqus_environment_file = 'abaqus_v6.env'
_abaqus_environment_extension = f".{_abaqus_environment_file}"
_stdout_extension = ".stdout"
