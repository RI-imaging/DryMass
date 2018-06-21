.. _sec_configuration_file:

==================
Configuration file
==================
The DryMass configuration file *drymass.cfg* is located in the
root of the output folder ("*_dm*" appended to the data path).
The configuration file is divided into sections.


.. _config_bg:

[bg] Background correction
--------------------------
DryMass uses the Python library :ref:`qpimage <qpimage:index>` for
background correction. For detailed information on the
algorithms (and the corresponding keyword arguments) used,
please see :mod:`qpimage.bg_estimate`.

.. include_definition:: bg


.. _config_meta:

[holo] Hologram analysis
------------------------
These parameters tune the analysis of off-axis hologram data (if applicable).
The parameters shown are passed to :func:`qpimage.holo.get_field`.

.. include_definition:: holo


[meta] Image meta data
----------------------
This section contains meta data of the experiment.

.. include_definition:: meta


.. _config_output:

[output] Supplementary data output
----------------------------------
This section defines what additional data are written to disk.

.. include_definition:: output


.. _config_roi:

[roi] Extraction of regions of interest
---------------------------------------
The extraction of ROIs is done in :func:`drymass.extractroi.extract_roi`.

.. include_definition:: roi


.. _config_specimen:

[specimen] Specimen parameters
------------------------------
Prior information about the analyzed object(s).

.. include_definition:: specimen


.. _config_sphere:

[sphere] Sphere-based image analysis
------------------------------------
Retrieval of refractive index and radius is done with the Python module
:ref:`qpsphere <qpsphere:index>`. The parameters either apply to 
:func:`qpsphere.edgefit.contour_canny` or to
:func:`qpsphere.imagefit.alg.match_phase`, depending on
:ref:`which analysis approach <qpsphere:choose_method_model>` is used.

.. include_definition:: sphere
