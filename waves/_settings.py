import pathlib

# Set some semi-private project meta variables for package internal use to avoid hardcode duplication
_project_root_abspath = pathlib.Path(__file__).parent.resolve()
_project_name_short = _project_root_abspath.name.upper()
_project_name = f"{_project_name_short} Analysis for Verified Engineering Simulations"
_abaqus_environment_file = "abaqus_v6.env"
_abaqus_environment_extension = f".{_abaqus_environment_file}"
_abaqus_solver_common_suffixes = [".odb", ".dat", ".msg", ".com", ".prt"]
_matlab_environment_extension = ".matlab.env"
_scons_command = "scons"
_scons_visualize_arguments = ["-Q", "--tree=status", "-n"]
_scons_tree_status = {'E': 'exists', 'R': 'exists in repository only', 'b': 'implicit builder', 'B': 'explicit builder',
                      'S': 'side effect', 'P': 'precious', 'A': 'always build', 'C': 'current', 'N': 'no clean',
                      'H ': 'no cache'}
_scons_substfile_suffix = ".in"
_stdout_extension = ".stdout"
_hash_coordinate_key = "parameter_set_hash"
_set_coordinate_key = "parameter_sets"
_quantiles_attribute_key = "_quantiles"
_cd_action_prefix = 'cd ${TARGET.dir.abspath} &&'
_installed_docs_index = _project_root_abspath / "docs/index.html"
_installed_quickstart_directory = _project_root_abspath / "quickstart"
_supported_scipy_samplers = ["Sobol", "Halton", "LatinHypercube", "PoissonDisk"]
_supported_salib_samplers = ["latin", "fast_sampler", "sobol", "finite_diff", "morris"]
_fetch_exclude_patterns = ["__pycache__", ".pyc", ".sconf_temp", ".sconsign.dblite", "config.log"]
_fetch_subdirectories = ["quickstart", "tutorials"]
_visualize_exclude = ["/usr/bin"]
_visualize_default_height = 12
_visualize_default_width = 36

# For lazy devs who want to test the ``waves quickstart`` CLI without an editable install...
# Enables ``python -m waves.main quickstart ...`` execution from repository root directory
_repository_quickstart_directory = _project_root_abspath.parent / _fetch_subdirectories[0] 
if not _installed_quickstart_directory.exists() and _repository_quickstart_directory.exists():
    _installed_quickstart_directory = _repository_quickstart_directory
