####################
Compression: Nominal
####################

**********
Simulation
**********

.. include:: simulation_description.txt

A continuum plain stress (CPS4) element type is used for the single element model. The nominal mesh is 1 element for the
square geometry, but this can be parameterized by the journal file :mod:`eabm_package.abaqus.single_element_mesh`. More
about Abaqus continuum elements can be found in the Abaqus documentation section titled "Solid Continuum Elements"
:cite:`ABAQUS`.

.. include:: simulation_material.txt

*******
Results
*******

.. figure:: stress_strain_comparison.*
   :align: center

   Stress-strain

***********
Conclusions
***********

.. include:: nominal_conclusions.txt
