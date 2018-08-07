============
Theory Notes
============

.. toctree::
  :maxdepth: 2


.. _section_theory_dry_mass:

Computation of cell dry mass
============================
The concept of cell dry mass computation was first introduced by Barer
:cite:`Barer1952`. The dry mass :math:`m` of a biological cell is defined
by its non-aqueous fraction :math:`f(x,y,z)` (concentration or density in g/L),
i.e. the number of grams of protein and DNA within the cell volume
(excluding salts).

.. math::

  m = \iiint f(x,y,z) \, dx dy dz

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


For a discrete image, this formula simplifies to

.. math::
  :label: drymass

  m_\text{med=intra} = \frac{\lambda}{2 \pi \alpha} \cdot \Delta A \cdot \sum_{i,j} \phi(x_i,y_j)
 
with the pixel area :math:`\Delta A` and a pixel-wise summation of the phase data.


Relative and absolute dry mass
==============================
If however the medium surrounding the cell has a different refractive index
(:math:`n_\text{med} \neq n_\text{intra}`), then the phase :math:`\phi`
is measured relative to the RI of the medium :math:`n_\text{med}`
which causes an underestimation of the dry mass if
:math:`n_\text{med} > n_\text{intra}`. For instance, a cell could
be immersed in a protein solution or embedded in a hydrogel with a refractive
index of :math:`n_\text{med}` = :math:`n_\text{intra}` + 0.002.
For a spherical cell with a radius of 10µm, the resulting dry mass is
underestimated by 46pg. Therefore, it is called "relative dry mass" :math:`m_\text{rel}`.

.. python code for example
   m = 350e-12
   r = 10e-6
   alpha = .18e-6
   n = 1.35
   m1 = (n - 1.335)/(3 * alpha) * 4 * np.pi * (r**3)
   m2 = (n - 1.337)/(3 * alpha) * 4 * np.pi * (r**3)
   msuppressed1 = m2 - m1
   # or
   msuppressed2 = (1.337 - 1.335)/(3 * alpha) * 4 * np.pi * (r**3)

.. math::

  m_\text{rel} = \frac{\lambda}{2 \pi \alpha} \cdot \iint \phi(x,y) \, dx dy,
 
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



Range of validity
=================
Variations in the refraction increment may occur and
thus the above considerations are not always valid.
For a detailed discussion of the variables that affect the
refraction increment, please see :cite:`Barer1954`.


Dependency on imaging wavelength
--------------------------------
Barer and Joseph measured the refraction increment of several proteins
in dependence of wavelength. In general, short wavelengths (366nm) yield
values close to 0.200mL/g while long wavelengths (656nm) yield smaller values
close to 0.180mL/g (table 3 in :cite:`Barer1954`).


Dependency on protein concentration
-----------------------------------
The refraction increment has been reported to be linear for a wide range of
protein concentrations. Barer and Joseph found that bovine serum albumin
exhibits a linear refraction increment up to its limit of solubility (figure 2
in :cite:`Barer1954`). They additionally received a personal communication
stating that this is also the case for gelatin.


Dependency on pH, temperature, and salts
----------------------------------------
The refraction increment is little dependent on pH, temperature, and salts
:cite:`Barer1954`.



Refraction increment and the mass of cells
------------------------------------------
Dry mass and actual mass of a cell differ by the weight of the intracellular
fluid. This weight difference is defined by the volume of the cell minus the
volume of the protein and DNA content. While it seems to be difficult to define
a partial specific volume (PSV) for DNA, there appears to be a consensus
regarding the PSV of proteins, yielding approximately 0.73mL/g
(see e.g. reference :cite:`Barer1957` as well as :cite:`Harpaz1994` and
`question 843 of the O-manual <http://msg.ucsf.edu/local/programs/ono/manuals/ofaq//Q.843.html>`_
referring to it). For example, the protein and DNA of a cell with a radius of 10µm
and a dry mass of 350pg (cell volume 4.19pL, average refractive index 1.35) occupy
approximately 0.73mL/g · 350pg = 0.256pL (assuming the PSV of protein and DNA are similar).
Therefore, the actual volume of the intracellular fluid is 3.93pL (94% of the cell volume)
which is equivalent to a mass of 3.93ng resulting in a total (actual) cell mass of 4.28ng.
Thus, the dry mass of this cell makes up approximately 10% of its actual mass which leads to
a total mass that is about 2% heavier than the equivalent volume of pure water (4.19ng).

.. python code for example:
   m_g = 350e-12
   r_m = 10 * 1e-6
   alpha = .18
   alpha_m3g = alpha * 1e-6
   n = 1.335 + 3 * alpha_m3g * m_g / (4 * np.pi * (r_m**3))
   # 1.3500401421221842
   volume = 4/3.*np.pi*r_m**3
   # 4.188790204786389e-15 m^3
   # = 4.188790204786389e-12 L
   m_water = 3.934e-12 * 1 * 1000



Default parameters in DryMass
=============================
- **The default refraction increment** is
  :math:`\alpha` = 0.18mL/g, as
  suggested for cells based on the refraction increment of cellular
  constituents by references :cite:`Barer1954` and :cite:`Barer1953`.
  The refraction increment can be manually set using the
  :ref:`configuration <sec_configuration_file>` key
  "refraction increment" in the "sphere" section.

- **The default refractive index of the intracellular fluid** in DryMass is assumed to be
  :math:`n_\text{intra}` = 1.335, an educated guess based on the refractive index
  of phosphate buffered saline (PBS), whose osmolarity and ion concentrations
  match those of the human body.
   