==============
Code reference
==============

.. toctree::
  :maxdepth: 2


cli.parse_funcs
===============
These methods are used to parse the values set in the
:ref:`sec_configuration_file` and convert them to the correct type.

.. automodule:: drymass.cli.parse_funcs
   :members:


roi
===
The :class:`ROIManager` class is used to manage and save/load ROI positions.

.. ipython::

    In [0]: from drymass.roi import ROIManager
    
    In [1]: rmg = ROIManager(identifier="example")
    
    In [2]: rmg.add(roislice=(slice(10, 100), slice(50, 140)),
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

.. autoclass:: drymass.roi.ROIManager
    :members:

.. autoclass:: drymass.roi.ROIManagerWarnging
