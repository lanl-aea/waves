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

.. include:: simulation_material.txt

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

The stress-strain plot shows that the simulation model is acting as expected with a linear elastic response through a
10% compressive strain load.

***********
Future Work
***********
