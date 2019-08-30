==============
Code reference
==============

.. toctree::
  :maxdepth: 2



Command-line interface
======================
The usage of the command line interface is described in detail
:ref:`here <section_command_line_interface>`. It consists of these
main methods:

.. automodule:: drymass.cli
    :members:
    :undoc-members:


cli.config
----------
.. automodule:: drymass.cli.config
    :members:
    :undoc-members:


cli.definitions
---------------
.. data:: drymass.cli.definitions.config
    
    The keys and subkeys of the definition dictionary are defined and
    described in the :ref:`configuration file section <sec_configuration_file>`.

cli.dialog
----------
The dialog submodule contains methods for user-interaction.

.. automodule:: drymass.cli.dialog
    :members:

cli.parse_funcs
---------------
These methods are used to parse the values set in the
:ref:`sec_configuration_file` and convert them to the correct type.

.. automodule:: drymass.cli.parse_funcs
   :members:

cli.plot
--------
DryMass plotting functionalities.

.. automodule:: drymass.cli.plot
   :members:


Data analysis
=============

anasphere
---------
.. automodule:: drymass.anasphere
    :members:

converter
---------
.. automodule:: drymass.converter
    :members:

extractroi
----------
.. automodule:: drymass.extractroi
    :members:


Helper classes and methods
==========================

search
------
.. automodule:: drymass.search
    :members:


threshold
---------
.. automodule:: drymass.threshold
    :members:


util
----
.. automodule:: drymass.util
    :members:


roi
---
The :class:`ROIManager` class is used to manage and save/load ROI positions.

.. ipython::

    In [0]: from drymass.roi import ROIManager
    
    In [1]: rmg = ROIManager(identifier="example")
    
    In [2]: rmg.add(roi_slice=(slice(10, 100), slice(50, 140)),
       ...:         image_index=2,
       ...:         roi_index=0,
       ...:         identifier="example_subroi_2.0")
       ...:

    In [3]: rmg.get_from_image_index(2)

Saving and loading can be done with:

.. ipython::

    In [4]: rmg.save("output_rois.txt")

    In [5]: rmg2 = ROIManager(identifier="ex")

    In [6]: rmg2.load("output_rois.txt")

And the content of "output_rois.txt" is:

.. include:: output_rois.txt
    :literal:

.. automodule:: drymass.roi
    :members:

