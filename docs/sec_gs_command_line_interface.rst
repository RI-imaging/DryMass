.. _section_command_line_interface:

======================
Command line interface
======================

.. toctree::
  :maxdepth: 2


DryMass comes with a command line interface (CLI). To use the CLI,
a command shell is required, such as the command prompt
`Cmd.exe <https://en.wikipedia.org/wiki/Cmd.exe>`_ on Windows,
or `Terminal.app <https://en.wikipedia.org/wiki/Terminal_(macOS)>`_ on MacOS.
Please note that if DryMass is installed in a
`virtual environment <https://docs.python.org/3/tutorial/venv.html>`_, then the
DryMass CLI is only available if this environment is activated.


.. _section_dm_convert:

dm_convert
----------
This command converts experimental data on disk to the TIF file format
for use with `Fiji/ImageJ <https://fiji.sc/>`_ and to the hdf5-based
`qpimage <https://qpimage.readthedocs.io/en/stable>`_ data file format.
The experimental data files are loaded with the
`qpformat <http://qpformat.readthedocs.io/en/stable/>`_ library, which
supports :ref:`several quantitative phase imaging file formats 
<qpformat:supported_formats>`. If a specific
format is not supported, please create an issue at the `qpformat issue
page <https://github.com/RI-imaging/qpformat/issues>`_. A typical use
case of dm_convert on Windows is

.. code-block:: bat

  dm_convert "d:\\data\path\to\experiment"

which is equivalent to

.. code-block:: bat

  d:
  cd "data\path\to"
  dm_convert experiment

If this command is run initially for an experimental data set, the user
is asked to enter or confirm imaging wavelength and detector pixel size.
Then, a new directory ``d:\\data\path\to\experiment_dm`` is created
with the following files:

*drymass.cfg*
  the user-editable :doc:`drymass configuration file <sec_gs_configuration_file>`
  which is used in subsequent analysis steps

*sensor_data.h5*
  the experimental data (including meta data) in the hdf5-based
  `qpimage <https://qpimage.readthedocs.io/en/stable>`_
  data file format

*sensor_data.tif*
  the experimental phase and amplitude series data as a tif file,
  importable in `Fiji/ImageJ <https://fiji.sc/>`_

Note that it is possible to edit the *drymass.cfg* file and to re-run the
dm_convert command (or any other of the commands below) with these updated
parameters.


.. _section_dm_extract_roi:

dm_extract_roi
--------------
This command automatically finds and extracts regions of interest (ROIs)
and performs an automated background correction for single-cell analysis.
The usage is the same as that of dm_convert:

.. code-block:: bat

  dm_extract_roi "d:\\data\path\to\experiment"

The command dm_extract_roi automatically runs dm_convert if it has not been
run before. If ROI detection fails, the search parameters have to manually
be updated in the :doc:`drymass configuration file <sec_gs_configuration_file>`. The most
important parameter is the diameter of the specimen in microns ("*size um*"
in the :ref:`specimen <config_specimen>` section);
all other parameters are defined in the :ref:`roi <config_roi>`
section. Note that the default parameters for the
:ref:`roi <config_roi>` section
are not written to the configuration file until dm_extract_roi is run.
The following files are created by dm_extract_roi:

*roi_data.h5*
  the extracted, background-corrected ROI data
  (including meta data) in the hdf5-based
  `qpimage <https://qpimage.readthedocs.io/en/stable>`_
  data file format

*roi_data.tif*
  the extracted, background-corrected ROI data as a tif file,
  importable in `Fiji/ImageJ <https://fiji.sc/>`_

*roi_slices.txt*
  the locations of the ROIs found as a txt file

*sensor_roi_images.tif*
  rendered sensor phase images with labeled ROIs;
  only created if "*roi images*" is set to "*True*"
  in the :ref:`output <config_output>` section of the
  :doc:`drymass configuration file <sec_gs_configuration_file>`


.. _section_dm_analyze_sphere:

dm_analyze_sphere
-----------------
This command is used for the analysis of spherical phase objects
such as liquid droplets, beads, or suspended cells. The basic
principle is thoroughly described in reference :cite:`Schuermann2016`.
In short, this approach assumes that the objects found with dm_extract_roi
are homogeneous and spherical which allows to extract parameters such as
radius and refractive index from a single phase image (as opposed to
tomographic approaches that require an acquisition of multiple phase
images from different directions). The parameters for the sphere analysis,
such as analysis method and scattering model,
are defined in the :ref:`sphere <config_sphere>` section of the 
:doc:`drymass configuration file <sec_gs_configuration_file>`. For an overview
of the available models, please refer to the
:ref:`qpsphere docs <qpsphere:choose_method_model>`. 
The following files are created by dm_analyze_sphere
(`METHOD` is the analysis method and `MODEL` is the
scattering model defined in *drymass.cfg*):

*sphere_METHOD_MODEL_data.h5*
  the quantitative sphere simulation data using `MODEL` with the
  parameters obtained with the combination of `METHOD` and `MODEL`
  for each of the ROIs obtained with dm_extract_roi in the hdf5-based
  `qpimage <https://qpimage.readthedocs.io/en/stable>`_
  data file format

*sphere_METHOD_MODEL_images.tif*
  rendered phase and intensity images of the input ROIs and the
  corresponding simulation, a difference, and a line plot through
  the phase image for visual inspection as a tif file,
  importable in `Fiji/ImageJ <https://fiji.sc/>`_

*sphere_METHOD_MODEL_statistics.txt*
  the analysis results, including refractive index, radius, and :ref:`relative and
  absolute dry mass <section_theory_dry_mass>` as a text file.
