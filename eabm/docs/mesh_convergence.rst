#############################
Compression: Mesh Convergence
#############################

**********
Simulation
**********

.. include:: simulation_description.txt

A continuum plain strain (CPE4) element type is used for the single element model. The mesh convergence study varies the
mesh seed size through the ``global_seed`` parameter used by :mod:`eabm_package.abaqus.single_element_mesh`. The mesh
convergence study includes four seed sizes in the table below.

.. table:: Mesh convergence parameters
   :align: center

   ================= ============================
   **Parameter Set** **global seed** :math:`[mm]`
   ----------------- ----------------------------
   0                 1.0
   1                 0.5
   2                 0.25
   3                 0.125
   ================= ============================

.. include:: simulation_material.txt

*******
Results
*******

.. only:: html

   .. figure:: mesh_convergence_stress.png
      :align: center

      Stress mesh convergence

.. only:: latex

   .. figure:: mesh_convergence_stress.pdf
      :align: center

      Stress mesh convergence

***********
Conclusions
***********

As expected from the simple loading and boundary conditions, the mesh convergence study shows that the quantity of
interest (QoI), stress in the loading direction, converges with a single element. This verifies that the parameterized
implementation of the load and boundary conditions correctly handles the mesh density and provides confidence in the
simulation journal files for applications to future parameter studies of material properties and load.

***********
Future Work
***********

Future work will apply more complex material models and a template sensitivity study between a more realistic QoI,
structural strength, and the parameterized geometry, and material parameters. Following a sensitivity study, uncertainty
propagation (UP) may be performed with representative bounds on input uncertainty, which will be stand in templates for
known experimental measurement uncertain on the input parameters.
