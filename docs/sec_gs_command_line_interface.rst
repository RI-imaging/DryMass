.. _section_command_line_interface:

======================
Command-line interface
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



.. _section_cli_basic:

Basic commands
==============

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


.. _section_cli_advanced:

Advanced usage
==============

Profile management with dm_profile
----------------------------------
If some of the parameters (e.g. pixel size or wavelength) are not stored
with the experimental data, DryMass will ask the user to enter these
in the command prompt. This process can be time-consuming, especially if a
recursive analysis is performed (see below). To simplify the analysis
in such cases, DryMass has the command ``dm_profile``, which allows
to store existing DryMass configuration files in a local library and
use them to analyze data.

.. code-block:: bat

    # add a profile named "preset2018a"
    dm_profile add preset2018a "d:\\data\path\to\experiment_dm\drymass.cfg"
    # list all profiles within the local library (name and path will be shown)
    dm_profile list
    # remove the profile "preset2018a"
    dm_profile remove preset2018a
    # export all local profiles to a folder
    dm_profile export "d:\\exported_profiles"

To use a profile stored in the local library for an analysis, simply pass
its name with the command-line parameter ``--profile``:

.. code-block:: bat

  dm_extract_roi --profile preset2018a "d:\\data\path\to\another\experiment"

Alternatively, a configuration file may also be specified without adding
it to the local library:

.. code-block:: bat

  dm_extract_roi --profile "d:\\data\path\to\experiment_dm\drymass.cfg" "d:\\data\path\to\another\experiment"

Note that the parameters in the profile are merged with the parameters
in the configuration file of the analyzed data. In other words, if a
parameter is missing in the profile, the parameter of the existing
`drymass.cfg` is used. If it is not in `drymass.cfg` the default
value is used.

Recursive analysis
------------------
By default, the basic analysis commands only accept a single measurement
as an argument. If there are several measurements, e.g.

- ``d:\\data\path\to\experiments\1``
- ``d:\\data\path\to\experiments\2``
- ``d:\\data\path\to\experiments\3``
- ``d:\\data\path\to\experiments\4``
- ``d:\\data\path\to\experiments\5``
- ...

then the command-line parameter ``--recursive`` can be used:

.. code-block:: bat

  dm_extract_roi --recursive "d:\\data\path\to\experiments"

The ``--recursive`` parameter can also be combined with the ``--profile``
parameter, which allows for a largely automated analysis pipeline:

.. code-block:: bat

  dm_extract_roi --recursive --profile preset2018a "d:\\data\path\to\experiments"
