import typing
import pathlib

# Set some semi-private project meta variables for package internal use to avoid hardcode duplication
_project_root_abspath = pathlib.Path(__file__).parent.resolve()
_project_name_short = _project_root_abspath.name.upper()
_project_name = f"{_project_name_short} Analysis for Verified Engineering Simulations"

# SCons extensions
_abaqus_environment_file = "abaqus_v6.env"
_abaqus_environment_extension = f".{_abaqus_environment_file}"
_abaqus_common_extensions = (".odb", ".dat", ".msg", ".com", ".prt")
_abaqus_datacheck_extensions = (".odb", ".dat", ".msg", ".com", ".prt", ".023", ".mdl", ".sim", ".stt")
_abaqus_explicit_extensions = (".odb", ".dat", ".msg", ".com", ".prt", ".sta")
_abaqus_explicit_restart_extensions = (".odb", ".prt", ".mdl", ".sim", ".stt", ".res", ".abq", ".pac", ".sel")
_abaqus_standard_extensions = (".odb", ".dat", ".msg", ".com", ".prt", ".sta")
_abaqus_standard_restart_extensions = (".odb", ".prt", ".mdl", ".sim", ".stt", ".res")
_matlab_environment_extension = ".matlab.env"
_sbatch_wrapper_options = "--wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap"
_sierra_environment_extension = ".env"
_scons_command = "scons"
_scons_tree_status = {
    "E": "exists",
    "R": "exists in repository only",
    "b": "implicit builder",
    "B": "explicit builder",
    "S": "side effect",
    "P": "precious",
    "A": "always build",
    "C": "current",
    "N": "no clean",
    "H ": "no cache",
}
_scons_substfile_suffix = ".in"
_stdout_extension = ".stdout"
_cd_action_prefix = "cd ${TARGET.dir.abspath} &&"
_redirect_action_suffix = "> ${TARGETS[-1].abspath} 2>&1"
_redirect_environment_suffix = "> ${TARGETS[-2].abspath} 2>&1"

# Parameter generators
_template_delimiter = "@"
_template_placeholder = f"{_template_delimiter}number"
_default_set_name_template = f"parameter_set{_template_placeholder}"
_default_previous_parameter_study = None
_default_require_previous_parameter_study = False
_default_overwrite = False
_default_dry_run = False
_default_write_meta = False
_default_output_file_template = None
_default_output_file = None
_parameter_study_meta_file = "parameter_study_meta.txt"
_allowable_output_file_typing = typing.Literal["h5", "yaml"]
_allowable_output_file_types = typing.get_args(_allowable_output_file_typing)
_default_output_file_type_api = _allowable_output_file_types[0]
_default_output_file_type_cli = _allowable_output_file_types[1]
_hash_coordinate_key = "set_hash"
_set_coordinate_key = "set_name"
_installed_docs_index = _project_root_abspath / "docs/index.html"
_modsim_template_directory = _project_root_abspath / "modsim_template"
_tutorials_directory = _project_root_abspath / "tutorials"
_supported_scipy_samplers = ["Sobol", "Halton", "LatinHypercube", "PoissonDisk"]
_supported_salib_samplers = ["latin", "fast_sampler", "sobol", "finite_diff", "morris"]
_cartesian_product_subcommand = "cartesian_product"
_custom_study_subcommand = "custom_study"
_latin_hypercube_subcommand = "latin_hypercube"
_sobol_sequence_subcommand = "sobol_sequence"
_one_at_a_time_subcommand = "one_at_a_time"
_parameter_study_subcommands = (
    _cartesian_product_subcommand,
    _custom_study_subcommand,
    _latin_hypercube_subcommand,
    _sobol_sequence_subcommand,
    _one_at_a_time_subcommand,
)
_parameter_study_description = (
    "Generates parameter studies in various output formats. Writes parameter study to STDOUT by default. If an "
    "output file template is specified, output one file per parameter set. Output file(s) are written if the file "
    "doesn't exist and overwritten when the file contents have changed. The overwrite option will always overwrite "
    "all files. The dry run option will print a list of files and contents that would have been  written."
)

# Fetch
_allowable_tutorial_numbers_typing = typing.Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
_allowable_tutorial_numbers = typing.get_args(_allowable_tutorial_numbers_typing)
_fetch_exclude_patterns = ["__pycache__", ".pyc", ".sconf_temp", ".sconsign.dblite", "config.log"]
_fetch_subdirectories = ["modsim_template", "modsim_template_2", "tutorials"]
_tutorial_paths = {
    0: [pathlib.Path("tutorials/tutorial_00_SConstruct")],
    1: [
        pathlib.Path("tutorials/modsim_package/__init__.py"),
        pathlib.Path("tutorials/modsim_package/abaqus/__init__.py"),
        pathlib.Path("tutorials/modsim_package/abaqus/rectangle_geometry.py"),
        pathlib.Path("tutorials/tutorial_01_geometry"),
        pathlib.Path("tutorials/tutorial_01_geometry_SConstruct"),
    ],
    2: [
        pathlib.Path("tutorials/modsim_package/abaqus/rectangle_partition.py"),
        pathlib.Path("tutorials/modsim_package/abaqus/rectangle_mesh.py"),
        pathlib.Path("tutorials/modsim_package/abaqus/abaqus_utilities.py"),
        pathlib.Path("tutorials/tutorial_02_partition_mesh"),
        pathlib.Path("tutorials/tutorial_02_partition_mesh_SConstruct"),
    ],
    3: [
        pathlib.Path("tutorials/modsim_package/abaqus/parts.inp"),
        pathlib.Path("tutorials/modsim_package/abaqus/assembly.inp"),
        pathlib.Path("tutorials/modsim_package/abaqus/boundary.inp"),
        pathlib.Path("tutorials/modsim_package/abaqus/field_output.inp"),
        pathlib.Path("tutorials/modsim_package/abaqus/history_output.inp"),
        pathlib.Path("tutorials/modsim_package/abaqus/materials.inp"),
        pathlib.Path("tutorials/modsim_package/abaqus/rectangle_compression.inp"),
        pathlib.Path("tutorials/tutorial_03_solverprep"),
        pathlib.Path("tutorials/tutorial_03_solverprep_SConstruct"),
    ],
    4: [
        pathlib.Path("tutorials/tutorial_04_simulation"),
        pathlib.Path("tutorials/tutorial_04_simulation_SConstruct"),
    ],
    5: [
        pathlib.Path("tutorials/modsim_package/abaqus/rectangle_compression.inp.in"),
        pathlib.Path("tutorials/tutorial_05_parameter_substitution"),
        pathlib.Path("tutorials/tutorial_05_parameter_substitution_SConstruct"),
    ],
    6: [
        pathlib.Path("tutorials/modsim_package/python/__init__.py"),
        pathlib.Path("tutorials/modsim_package/python/rectangle_compression_nominal.py"),
        pathlib.Path("tutorials/tutorial_06_include_files"),
        pathlib.Path("tutorials/tutorial_06_include_files_SConstruct"),
    ],
    7: [
        pathlib.Path("tutorials/modsim_package/python/rectangle_compression_cartesian_product.py"),
        pathlib.Path("tutorials/tutorial_07_cartesian_product"),
        pathlib.Path("tutorials/tutorial_07_cartesian_product_SConstruct"),
    ],
    8: [
        pathlib.Path("tutorials/tutorial_08_data_extraction"),
        pathlib.Path("tutorials/tutorial_08_data_extraction_SConstruct"),
    ],
    9: [
        pathlib.Path("tutorials/modsim_package/python/post_processing.py"),
        pathlib.Path("tutorials/tutorial_09_post_processing"),
        pathlib.Path("tutorials/tutorial_09_post_processing_SConstruct"),
    ],
    10: [
        pathlib.Path("tutorials/modsim_package/python/regression.py"),
        pathlib.Path("tutorials/modsim_package/python/tests/test_regression.py"),
        pathlib.Path("tutorials/unit_testing"),
        pathlib.Path("tutorials/tutorial_10_unit_testing_SConstruct"),
    ],
    11: [
        pathlib.Path("tutorials/modsim_package/python/rectangle_compression_cartesian_product.csv"),
        pathlib.Path("tutorials/tutorial_11_regression_testing"),
        pathlib.Path("tutorials/tutorial_11_regression_testing_SConstruct"),
    ],
    12: [
        pathlib.Path(
            "tutorials/tutorial_12_archival",
        ),
        pathlib.Path("tutorials/tutorial_12_archival_SConstruct"),
    ],
}

# Visualize
_scons_visualize_arguments = ["-Q", "--tree=status", "-n"]
_visualize_exclude = ["/usr/bin"]
_visualize_default_height = 12
_visualize_default_width = 36
_visualize_default_font_size = 10
_default_sconstruct = pathlib.Path("SConstruct")
_default_node_color = "#5AC7CB"  # Light blue from Waves Logo
_default_edge_color = "#B7DEBE"  # Light green from Waves Logo

# Remove third-party packages from the project namespace
del pathlib
