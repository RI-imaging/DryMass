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

dm_convert
----------
This command converts experimental data on disk to the hdf5-based
`qpimage <https://qpimage.readthedocs.io/en/stable>`_ data file format.
The experimental data files are loaded with the
`qpformat <http://qpformat.readthedocs.io/en/stable/>`_ library, which
supports several quantitative phase imaging file formats. If a specific
format is not supported, please create an issue at the `qpimage issue
page <https://github.com/RI-imaging/qpformat/issues>`_. A typical use
case of dm_convert is

.. code-block:: bat

  dm_convert "d:\\data\path\to\experiment"

which is equivalent to

.. code-block:: bat

  d:
  cd "data\path\to"
  dm_convert experiment

If this command is run initially for an experimental data set, the user
is asked to enter or confirm imaging wavelength, detector pixel size,
and refractive index of the medium.
Then, a new directory ``d:\\data\path\to\experiment_dm`` is created
with the following files:

*drymass.cfg*
  the user-editable :doc:`drymass configuration file <configuration_file>`
  which is used in subsequent analysis steps

*sensor_data.h5*
  the experimental data (including meta data) in the hdf5-based
  `qpimage <https://qpimage.readthedocs.io/en/stable>`_
  data file format

*sensor_data.tif*
  the experimental phase and amplitude series data as a tif file,
  importable in `Fiji/ImageJ <https://fiji.sc/>`_

Note that it is possible to edit the *drymass.cfg* file and to re-run the
dm_convert command with these updated parameters.


dm_extract_roi
--------------



dm_analyze_sphere
-----------------



