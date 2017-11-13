==================
Configuration file
==================
The DryMass configuration file *drymass.cfg* is located in the
root of the output folder ("*_dm*" appended to the data path).
The configuration file is divided into sections.


Background correction ("bg")
----------------------------
.. literalinclude:: ../drymass/definitions.py
   :language: python
   :start-after: "bg"
   :end-before: }
   :dedent: 8


Extraction of regions of interest ("roi")
-----------------------------------------
.. literalinclude:: ../drymass/definitions.py
   :language: python
   :start-after: "roi"
   :end-before: }
   :dedent: 8


Image meta data ("meta")
------------------------
.. literalinclude:: ../drymass/definitions.py
   :language: python
   :start-after: "meta"
   :end-before: }
   :dedent: 8


User data output ("output")
---------------------------
.. literalinclude:: ../drymass/definitions.py
   :language: python
   :start-after: "output"
   :end-before: }
   :dedent: 8


Specimen parameters ("specimen")
--------------------------------
.. literalinclude:: ../drymass/definitions.py
   :language: python
   :start-after: "specimen"
   :end-before: }
   :dedent: 8


Sphere-based image analysis ("sphere")
--------------------------------------
.. literalinclude:: ../drymass/definitions.py
   :language: python
   :start-after: "sphere"
   :end-before: }
   :dedent: 8

