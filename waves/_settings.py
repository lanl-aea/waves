import pathlib

# Set some semi-private project meta variables for package internal use to avoid hardcode duplication
_project_root_abspath = pathlib.Path(__file__).parent.resolve()
_project_name_short = _project_root_abspath.name.upper()
_project_name = f"{_project_name_short} Analysis for Verified Engineering Simulations"
_abaqus_environment_file = "abaqus_v6.env"
_abaqus_environment_extension = f".{_abaqus_environment_file}"
_abaqus_solver_common_suffixes = [".odb", ".dat", ".msg", ".com", ".prt"]
_abaqus_datacheck_extensions = [".odb", ".dat", ".msg", ".com", ".prt", ".023", ".mdl", ".sim", ".stt"]
_abaqus_explicit_extensions = [".odb", ".dat", ".msg", ".com", ".prt", ".sta"]
_abaqus_standard_extensions = [".odb", ".dat", ".msg", ".com", ".prt", ".sta"]
_matlab_environment_extension = ".matlab.env"
_sbatch_wrapper_options = "--wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap"
_sierra_environment_extension = ".env"
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
_redirect_action_postfix = "> ${TARGET[-1].abspath} 2>&1"
_installed_docs_index = _project_root_abspath / "docs/index.html"
_modsim_template_directory = _project_root_abspath / "modsim_template"
_tutorials_directory = _project_root_abspath / "tutorials"
_supported_scipy_samplers = ["Sobol", "Halton", "LatinHypercube", "PoissonDisk"]
_supported_salib_samplers = ["latin", "fast_sampler", "sobol", "finite_diff", "morris"]
_fetch_exclude_patterns = ["__pycache__", ".pyc", ".sconf_temp", ".sconsign.dblite", "config.log"]
_fetch_subdirectories = ["modsim_template", "tutorials"]
_visualize_exclude = ["/usr/bin"]
_visualize_default_height = 12
_visualize_default_width = 36
_visualize_default_font_size = 10
_cartesian_product_subcommand = "cartesian_product"
_custom_study_subcommand = "custom_study"
_latin_hypercube_subcommand = "latin_hypercube"
_sobol_sequence_subcommand = "sobol_sequence"
_parameter_study_subcommands = [
    _cartesian_product_subcommand,
    _custom_study_subcommand,
    _latin_hypercube_subcommand,
    _sobol_sequence_subcommand
]
_parameter_study_description = \
    "Generates parameter studies in various output formats. Writes parameter study to STDOUT by default. If an " \
    "output file template is specified, output one file per parameter set. Output file(s) are written if the file " \
    "doesn't exist and overwritten when the file contents have changed. The overwrite option will always overwrite " \
    "all files. The dry run option will print a list of files and contents that would have been  written. " \
    "The 'h5' output is the only output type that contains both the parameter " \
    "samples and quantiles."
