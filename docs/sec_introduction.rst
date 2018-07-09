============
Introduction
============

.. toctree::
  :maxdepth: 2


What is DryMass?
----------------
DryMass is a tool in quantitative phase imaging (QPI) for the
extraction of physical properties such as volume, refractive index,
and dry mass of pure phase objects. Features include

- automated extraction of meta data (e.g. wavelength, acquisition time) from experimental data files,
- automated detection of phase object positions (cells, beads, lipid droplets),
- elaborate methods for phase image background correction,
- determination of dry mass for biological cells, or
- extraction of refractive index and radius for spherical phase objects
  such as liquid droplets, microgel beads, or cells. 


What are typical use cases of DryMass?
--------------------------------------
The focus of DryMass is the analysis of large
data sets (e.g. > 10 cells). Here are a few examples:

- You have recorded several digital holograms and would like to
  extract phase and amplitude from them. When analyzing experimental
  data, DryMass automatically converts holograms (stored as .tif files)
  to phase and intensity image series, .tif files that can be opened
  with e.g. Fiji. You also have several options for automated
  phase/amplitude background correction.

- You are interested in characterizing microgel beads and recorded
  several quantitative phase images, each of
  them containing a few well-separated beads. By tuning only a few
  parameters, such as the expected specimen size, the phase image
  background correction method, or the scattering model, DryMass
  determines the position of the beads, and yields accurate values for
  refractive index, size, and dry mass for each bead.

- You would like to monitor cell dry mass over time. If the cells
  are well-separated, this task is trivial with DryMass. If in
  addition, the cells are spherical (e.g. suspended cells), then
  DryMass can also compute accurate values for mean refractive index
  and cell size.


Quantitative phase imaging
--------------------------
Quantitative phase imaging (QPI) is a 2D imaging technique that quantifies
the phase retardation of a wave traveling through a specimen.
For instance, digital holographic microscopy (DHM) :cite:`Kemper_2007` can be
used to record the quantitative phase image of biological cells, yielding the
optical density from which the :ref:`dry mass <section_theory_dry_mass>` or
the refractive index (RI) can be computed. Another example is electron holography
:cite:`Lehmann_2002` which can be used to visualize
`p-n junctions <https://en.wikipedia.org/wiki/P%E2%80%93n_junction>`_
due to the different electronic potentials in the doped semiconductors. 
DryMass was designed for the analysis of single cells (typical units for distance [µm]
and wavelength [nm]), but the concepts used apply to both methods.
