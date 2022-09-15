#######################
Single Element: Nominal
#######################

**********
Simulation
**********

The single element model is representative of the simplest model possible to exercise the capabilities of the workflow.
It is a single 2D square element oriented in the 1-2 plane consisting of a simple material model, simple boundary
conditions, and a simple uniaxial compression loading scheme. The simulation preparation and solve are conducted in
Abaqus :cite:`ABAQUS`.

.. figure:: waves_logo_brandmark_smaller.png
   :align: center

   Placeholder for simulation schematic

The single element model is comprised of a single 2D square part with nominal dimensions 1mm x 1mm, but which can be
parameterized by width and height by the journal file: :meth:`eabm_package.abaqus.single_element_geometry`.

The bottom left node of the geometry is restricted in all six translational/rotational degrees of freedom using an
encastre boundary condition. The bottom edge uses a roller boundary condition, with no translation in the 2 direction,
but is free to move in the 1 direction.

Loading is prescribed as a uniaxial displacement of the top edge of the part in the negative 2 direction (compression),
with a nominal displacement of 0.1mm, which can be parameterized in the workflow.

A continuum plain strain (CPE4) element type is used for the single element model. The nominal mesh is 1 element for the
square geometry, but this can be parameterized in :meth:`eabm_package.abaqus.single_element_mesh`. More about Abaqus
continuum elements can be found in the Abaqus documentation section titled "Solid Continuum Elements" :cite:`ABAQUS`.

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

***********
Conclusions
***********

***********
Future Work
***********
