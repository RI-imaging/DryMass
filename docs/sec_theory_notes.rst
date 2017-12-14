============
Theory Notes
============

.. toctree::
  :maxdepth: 2


.. _section_theory_dry_mass:

Computation of cell dry mass
============================
Definition
----------
The concept of cell dry mass computation was first introduced by Barer
:cite:`Barer_1952`. The dry mass :math:`m` of a biological cell is defined
by its non-aqueous fraction :math:`f(x,y,z)`, i.e. the number of grams of
dry proteins and DNA within the cell volume (excluding salts).

.. math::

  m = \iiint f(x,y,z) \, dx dy dz \\

The assumption of dry mass computation in QPI is that :math:`f(x,y,z)`
is proportional to the RI of the cell :math:`n(x,y,z)` with a proportionality
constant called the refraction increment :math:`\alpha` (units [mL/g])

.. math::

  n(x,y,z) = n_\text{intra} + \alpha f(x,y,z)

with the RI of the intracellular fluid :math:`n_\text{intra}`,
a dilute salt solution. These two equations can be combined to

.. math::
  :label: intmass
  
  m = \frac{1}{\alpha} \cdot \iiint (n(x,y,z) - n_\text{intra}) \, dx dy dz.


In QPI, the RI is measured indirectly
as a projected quantitative phase retardation image :math:`\phi(x,y)`.

.. math::

  \phi(x,y) = \frac{2 \pi}{\lambda} \int (n(x,y,z) - n_\text{med}) \, dz

with the vacuum wavelength :math:`\lambda` of the imaging light and the
refractive index of the cell-embedding medium :math:`n_\text{med}`. 
Integrating the above equation over the detector area :math:`(x,y)` yields

.. math::
  :label: phiri

  \iint \phi(x,y) \, dx dy = \frac{2 \pi}{\lambda} \iiint (n(x,y,z) - n_\text{med}) \, dx dy dz


If the embedding medium has the same refractive index as the intracellular solute
(:math:`n_\text{med} = n_\text{intra}`),
then equations :eq:`intmass` and :eq:`phiri` can be combined to

.. math::

  m_\text{med=intra} = \frac{\lambda}{2 \pi \alpha} \cdot \iint \phi(x,y) \, dx dy.

Relative and absolute dry mass
------------------------------
If however the medium surrounding the cell has a different refractive index
(:math:`n_\text{med} \neq n_\text{intra}`), then the phase :math:`\phi`
is measured relative to the RI of the medium :math:`n_\text{med}`
which causes an underestimation of the dry mass if
:math:`n_\text{med} > n_\text{intra}`. For instance, a cell could
be immersed in a protein solution or embedded in a hydrogel with a refractive
index of :math:`n_\text{med}` = :math:`n_\text{intra}` + 0.002.
The resulting error in dry mass made for a spherical cell with a constant
RI of 1.37 is 5\%. This mass is called "relative dry mass" :math:`m_\text{rel}`.

.. math::

  m_\text{rel} = \frac{\lambda}{2 \pi \alpha} \cdot \iint \phi(x,y) \, dx dy,
 
For a discrete image, this formula simplifies to

.. math::
  :label: drymass
  
  m_\text{rel} = \frac{\lambda}{2 \pi \alpha} \cdot \Delta A \cdot \sum_{i,j} \phi(x_i,y_j)
 
with the pixel area :math:`\Delta A` and a pixel-wise summation of the phase data.

If the imaged phase object is spherical with the radius :math:`R`,
then the "absolute dry mass" :math:`m_\text{abs}`
can be computed by splitting equation :eq:`intmass` into relative mass and suppressed 
spherical mass.
   
.. math::

  m_\text{abs} &= \frac{1}{\alpha} \cdot \iiint (n(x,y,z) - n_\text{med} + n_\text{med} - n_\text{intra}) \, dx dy dz \\
               &= m_\text{rel} + \frac{4\pi}{3\alpha} R^3 (n_\text{med} - n_\text{intra})

For a visualization of the deviation of the relative dry mass from the actual dry mass
for spherical objects, please have a look at the
:ref:`relative vs. absolute dry mass example <example_mass_relative_vs_absolute>`. 


Notes and gotchas
-----------------
- **The default refraction increment in DryMass** is
  :math:`\alpha` = 0.18 mL/g, as
  suggested for cells based on the refraction increment of cellular
  constituents by references :cite:`Barer_1954` and :cite:`Barer_1953`.
  The refraction increment can be manually set using the configuration key
  "refraction increment" in the "sphere" section.

- **Variations in the refraction increment** may occur and
  thus the above considerations are not always valid.
  The refraction increment is little dependent on pH and temperature, but may be
  strongly dependent on wavelength (e.g. serum albumin
  :math:`\alpha_\text{SA@366nm}` = 0.198 mL/g and
  :math:`\alpha_\text{SA@656nm}` = 0.179 mL/g) :cite:`Barer_1954`.


- **The refractive index of the intracellular fluid** in DryMass is assumed to be
  :math:`n_\text{intra}` = 1.335, an educated guess based on the refractive index
  of phosphate buffered saline (PBS), whose osmolarity and ion concentrations
  match those of the human body.

