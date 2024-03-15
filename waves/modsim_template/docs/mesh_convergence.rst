#############################
Compression: Mesh Convergence
#############################

**********
Simulation
**********

.. include:: simulation_description.txt

A continuum plain stress (CPS4) element type is used for the rectangle model. The mesh convergence study varies the
mesh seed size through the ``global_seed`` parameter used by :mod:`modsim_package.abaqus.rectangle_mesh`. The mesh
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

******
Theory
******

.. include:: theory.txt

*******
Results
*******

.. figure:: mesh_convergence_stress.png
   :align: center

   Stress mesh convergence

***********
Conclusions
***********

.. include:: mesh_convergence_conclusions.txt

***********
Future Work
***********

Future work will apply more complex material models and a template sensitivity study between a more realistic QoI,
structural strength, and the parameterized geometry, and material parameters. Following a sensitivity study, uncertainty
propagation (UP) may be performed with representative bounds on input uncertainty, which will be stand in templates for
known experimental measurement uncertain on the input parameters.
