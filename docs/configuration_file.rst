==================
Configuration file
==================
The DryMass configuration file *drymass.cfg* is located in the
root of the output folder ("*_dm*" appended to the data path).
The configuration file is divided into sections.

.. _config_bg:

[bg] Background correction
--------------------------
.. literalinclude:: ../drymass/definitions.py
   :language: python
   :start-after: "bg"
   :end-before: }
   :dedent: 8


.. _config_meta:

[meta] Image meta data
----------------------
.. literalinclude:: ../drymass/definitions.py
   :language: python
   :start-after: "meta"
   :end-before: }
   :dedent: 8


.. _config_roi:

[roi] Extraction of regions of interest
---------------------------------------
.. literalinclude:: ../drymass/definitions.py
   :language: python
   :start-after: "roi"
   :end-before: }
   :dedent: 8


.. _config_output:

[output] Supplemental data output
---------------------------------
.. literalinclude:: ../drymass/definitions.py
   :language: python
   :start-after: "output"
   :end-before: }
   :dedent: 8


.. _config_specimen:

[specimen] Specimen parameters
------------------------------
.. literalinclude:: ../drymass/definitions.py
   :language: python
   :start-after: "specimen"
   :end-before: }
   :dedent: 8


.. _config_sphere:

[sphere] Sphere-based image analysis
------------------------------------
.. literalinclude:: ../drymass/definitions.py
   :language: python
   :start-after: "sphere"
   :end-before: }
   :dedent: 8

