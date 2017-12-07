==================================
Refractive index of microgel beads
==================================

Introduction
------------
Microgel beads are transparent, homogeneous, and spherical objects
that are ideal test objects for quantitative phase imaging. The DryMass
command :ref:`section_dm_analyze_sphere` can estimate the average
refractive index of such homogeneous objects. This is a short tutorial
that will reproduce 
`supplementary figure 2a <https://arxiv.org/src/1706.00715v3/anc/S02_2D_phase_measurements.pdf>`_
of reference :cite:`Schuermann2017`.

Prerequisites
-------------
For this tutorial, you need:
- Python 3.5 or above and DryMass version 0.1.1 or above (see :ref:`section_install`)
- `Fiji <https://fiji.sc/>`_ (optional, for data visualization)
- Experimental data set: `QLSR_PAA_beads.zip <https://github.com/RI-imaging/QPI-data/raw/master/QLSR_PAA_beads.zip>`_


Executing dm_analyze_sphere
---------------------------
DryMass comes with a :ref:`section_command_line_interface` (CLI)
which is made available after the installation.
We will use the DryMass command  :ref:`section_dm_analyze_sphere`
to extract the refractive index values of a population of microgel
beads. Using the command shell of your operating system, navigate
to the location of
`QLSR_PAA_beads.zip <https://github.com/RI-imaging/QPI-data/raw/master/QLSR_PAA_beads.zip>`_
and execute the command ``dm_analyze_sphere`` with
``QLSR_PAA_beads.zip`` as an argument. You will be prompted for
the refractive index of the surrounding medium (1.335), the
detector pixel size in microns (0.14), and the wavelength in
nanometers (647). Simply type in these values (press the `Enter`
key to let DryMass acknowledge each input). On Windows, this
will look similar to this:

.. figure:: t01_analyze_sphere.gif


