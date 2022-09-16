#######################
Single Element: Nominal
#######################

**********
Simulation
**********

.. include:: simulation_description.txt

A continuum plain strain (CPE4) element type is used for the single element model. The nominal mesh is 1 element for the
square geometry, but this can be parameterized by the journal file :mod:`eabm_package.abaqus.single_element_mesh`. More
about Abaqus continuum elements can be found in the Abaqus documentation section titled "Solid Continuum Elements"
:cite:`ABAQUS`.

A mock material definition was developed using the following parameters in the mmNsK unit system:

.. table:: Material Parameters
   :align: center

   ================== ========= ==================
   **Parameter name** **Value** **Units**
   ------------------ --------- ------------------
   Density            2.7E-09   :math:`[Mg/mm^3]`
   Elastic Modulus    100       :math:`[MPa]`
   Poisson's Ratio    0.3       :math:`[-]`
   Specific Heat      8.96E08   :math:`[mJ/(MgK)]`
   Conductivity       132       :math:`[mW/(mmK)]`
   Thermal Expansion  23.58E-6  :math:`[1/K]`
   ================== ========= ==================

*******
Results
*******

.. only:: html

   .. figure:: stress_strain_comparison.png
      :align: center

      Stress-strain

.. only:: latex

   .. figure:: stress_strain_comparison.pdf
      :align: center

      Stress-strain

***********
Conclusions
***********

***********
Future Work
***********
