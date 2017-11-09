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
