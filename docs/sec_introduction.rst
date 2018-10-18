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


What is quantitative phase imaging?
-----------------------------------
Quantitative phase imaging (QPI) is a 2D imaging technique that quantifies
the phase retardation of a wave traveling through a specimen.
For instance, digital holographic microscopy (DHM) :cite:`Kemper2007a` can be
used to record the quantitative phase image of biological cells, yielding the
optical density from which the :ref:`dry mass <section_theory_dry_mass>` or
the refractive index (RI) can be computed. Another example is electron holography
:cite:`Lehmann2002` which can be used to visualize
`p-n junctions <https://en.wikipedia.org/wiki/P%E2%80%93n_junction>`_
due to the different electronic potentials in the doped semiconductors. 
DryMass was designed for the analysis of single cells (typical units for distance [µm]
and wavelength [nm]), but the concepts used apply to both methods.


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


How should I cite DryMass?
--------------------------
If you are using DryMass in a scientific publication, please
cite it with:

::

  (...) using DryMass version X.X.X (available at
  https://pypi.python.org/pypi/drymass).

or in a bibliography

::
  
  Paul Müller (2018), DryMass version X.X.X: Phase image analysis
  [Software]. Available at https://pypi.python.org/pypi/drymass.

and replace ``X.X.X`` with the version of DryMass that you used.

Furthermore, several ideas that DryMass builds upon have been described
and published in scientific journals:


- Retrieval of RI and radius using the OPD edge-detection approach
  is described in :cite:`Schuermann2015` and :cite:`Schuermann2016`
  (``method="edge"`` and ``model="projection"`` in the ``[sphere]``
  section of the :ref:`Configuration <sec_configuration_file>`).

- Retrieval of RI and radius by fitting 2D models (OPD projection,
  Rytov approximation, systematically corrected Rytov approximation,
  Mie) to phase images is described in :cite:`Mueller2018`.
  (``method="image"`` in the ``[sphere]``
  section of the :ref:`Configuration <sec_configuration_file>`).
