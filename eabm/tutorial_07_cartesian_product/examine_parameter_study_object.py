import sys
import pathlib

# Only required when WAVES is not installed as a package, e.g. for local testing in WAVES repository.
try:
    import waves
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))
    import waves

parameter_schema = {
    'width': [1, 1.1],
    'height': [1, 1.1],
    'global_seed': [1],
    'displacement': [-1],
}


parameter_set_file_template = "parameter_set@number"

parameter_generator = waves.parameter_generators.CartesianProduct(
    parameter_schema,
    output_file_template=parameter_set_file_template)
parameter_generator.generate()
parameter_study = parameter_generator.parameter_study

print(type(parameter_generator))
print(type(parameter_study))
print(parameter_study)
