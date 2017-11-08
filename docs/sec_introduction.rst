============
Introduction
============

.. toctree::
  :maxdepth: 2


What is DryMass?
----------------
DryMass is a software for quantitative phase imaging (QPI) analysis
with functionalities such as

- extraction of meta data (e.g. wavelength, acquisition time) from experimental data files,
- quantitative phase image background correction,
- determination of dry mass for biological cells, or
- extraction of refractive index and radius for spherical phase objects
  such as liquid droplets, microgel beads, or cells. 


Quantitative phase imaging
--------------------------
Quantitative phase imaging (QPI) is a 2D imaging technique that quantifies
the phase retardation of a wave traveling through a specimen.
For instance, digital holographic microscopy (DHM) :cite:`Kemper_2007` can be
used to record the quantitative phase image of biological cells, yielding the
optical density from which the dry mass (see below) or the refractive index (RI) can
be computed. Another example is electron holography :cite:`Lehmann_2002` which can
be used to visualize `p-n junctions <https://en.wikipedia.org/wiki/P%E2%80%93n_junction>`_
due to the different electronic potentials in the doped semiconductors. 
DryMass was designed for the single-cell analysis (typical units for distance [µm]
and wavelength [nm]), but the concepts used apply to both methods.


Computation of cell dry mass
----------------------------
The concept of cell dry mass computation was first introduced by Barer
:cite:`Barer_1952`. The dry mass :math:`m` of a biological cell is defined
by its non-aqueous fraction :math:`f(x,y,z)`, e.g. ions, proteins, and DNA.

.. math::

  m = \iiint f(x,y,z) \, dx dy dz \\

The assumption of dry mass computation in QPI is that :math:`f(x,y,z)`
is proportional to the RI of the cell :math:`n(x,y,z)` with a proportionality
constant called the refraction increment :math:`\alpha` (units [mL/g])

.. math::

  n(x,y,z) - n_\text{water} = \alpha f(x,y,z)

with the RI of water :math:`n_\text{water}` = 1.333.
In QPI, the RI is measured indirectly as a projected
quantitative phase retardation image :math:`\phi(x,y)`.

.. math::
  :label: phiri

  \phi(x,y) = \frac{2 \pi}{\lambda} \int (n(x,y,z) - n_\text{med}) \, dz

with the vacuum wavelength :math:`\lambda` of the imaging light. 
Integrating the above equation over the detector area :math:`(x,y)` yields

.. math::
  :label: intmass
  
  m = \frac{1}{\alpha} \cdot \iiint (n(x,y,z) - n_\text{water}) \, dx dy dz

in which equation :eq:`phiri` can be inserted. However, if the medium
surrounding the cell is not water (:math:`n_\text{med} \neq n_\text{water}`),
then the phase :math:`\phi`
is measured relative to the higher RI of the medium :math:`n_\text{med}`
which causes an underestimation of the dry mass. For instance, many cell
types are immersed in phosphate buffered saline (PBS) with an RI of 1.335.
The resulting error in dry mass made for a spherical cell with a constant
RI of 1.37 is 5\%. Therefore, the this mass is called
"relative dry mass" :math:`m_\text{rel}`.

.. math::

  m_\text{rel} = \frac{\lambda}{2 \pi \alpha} \cdot \iint \phi(x,y) \, dx dy.

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

  m_\text{abs} &= \frac{1}{\alpha} \cdot \iiint (n(x,y,z) - n_\text{med} + n_\text{med} - n_\text{water}) \, dx dy dz \\
               &= m_\text{rel} + \frac{4\pi}{3\alpha} R^3 (n_\text{med} - n_\text{water})


In DryMass, the default refraction increment is :math:`\alpha` = 0.18 mL/g, as
suggested for cells based on the refraction increment of cellular
constituents by references :cite:`Barer_1954` and :cite:`Barer_1953`.
The refraction increment can be manually set using the configuration key
"refraction increment" in the "sphere" section.

Please note that the above considerations are not always valid;
The refraction increment is little dependent on pH and temperature, but may be
strongly dependent on wavelength (e.g. serum albumin
:math:`\alpha_\text{SA@366nm}` = 0.198 mL/g and
:math:`\alpha_\text{SA@656nm}` = 0.179 mL/g) :cite:`Barer_1954`.

