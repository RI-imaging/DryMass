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
by its non-aqueous fraction :math:`f(x,y,z)`, e.g. proteins and DNA.

.. math::

  m = \iiint f(x,y,z) \, dx dy dz \\

The assumption of dry mass computation in QPI is that :math:`f(x,y,z)`
is proportional to the RI :math:`n(x,y,z)` with a proportionality
constant called the refraction increment :math:`\alpha` (units [mL/g])

.. math::

  n(x,y,z) - n_\text{med} = \alpha f(x,y,z)

with the RI of the surrounding medium :math:`n_\text{med}`. Note that this implies
that the dry mass is computed relative to the medium. If a large fraction of the medium
consists of e.g. proteins, then the dry mass of the sample is underestimated and
must be corrected using the (unknown) volume occupied by the sample.
For a thorough discussion on the relationship between mass density and RI, see
reference :cite:`Barer_1954`. In QPI, the RI is measured indirectly as a projected
quantitative phase retardation image :math:`\phi(x,y)`.

.. math::

  \phi(x,y) = \frac{2 \pi}{\lambda} \int (n(x,y,z) - n_\text{med}) \, dz

with the vacuum wavelength :math:`\lambda` of the imaging light. 
Integrating the above equation over the detector area :math:`(x,y)` yields

.. math::
  
  m = \frac{\lambda}{2 \pi \alpha} \cdot \iint \phi(x,y) \, dx dy.

For a discrete image, this formula simplifies to

.. math::
  
  m = \frac{\lambda}{2 \pi \alpha} \cdot \Delta A \cdot \sum_{i,j} \phi(x_i,y_j)
 
with the pixel area :math:`\Delta A` and a pixel-wise summation of the phase data.

In DryMass, the refraction increment is set to :math:`\alpha = 0.2 \text{mL/g}` by
default, an approximate average value for proteins and DNA that is commonly used in
literature :cite:`Popescu_2008`, :cite:`Schuermann_2016`. The refraction increment
can be manually modified using the configuration key "refraction increment" in the
"sphere" section.