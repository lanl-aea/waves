"""Parameter sets and schemas for the rectangle compression simulation

* nominal: simulation variables dictionary

  * width
  * height
  * global_seed
  * displacement

* mesh_convergence: WAVES CartesianProduct schema

  * global_seed
"""
nominal = {
    'width': 1.0,
    'height': 1.0,
    'global_seed': 1.0,
    'displacement': -0.01
}
mesh_convergence = {
    'global_seed': [1.0, 0.5, 0.25, 0.125],
}
