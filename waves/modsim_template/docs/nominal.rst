####################
Compression: Nominal
####################

**********
Simulation
**********

.. include:: simulation_description.txt

A continuum plain stress (CPS4) element type is used for the rectangle model. The nominal mesh is 1 element for the
square geometry, but this can be parameterized by the journal file :mod:`modsim_package.abaqus.rectangle_mesh`. More
about Abaqus continuum elements can be found in the Abaqus documentation section titled "Solid Continuum Elements"
:cite:`ABAQUS`.

.. include:: simulation_material.txt

******
Theory
******

.. include:: theory.txt

*******
Results
*******

.. figure:: stress_strain_comparison.png
   :align: center

   Stress-strain

***********
Conclusions
***********

.. include:: nominal_conclusions.txt
