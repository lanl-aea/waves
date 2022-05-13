simulation_variables = {
    'width': 1.0,
    'height': 1.0,
    'global_seed': 1.0,
    'displacement': -1.0
}
simulation_substitution_dictionary = {f"@{key}@": value for key, value in simulation_variables.items()}
