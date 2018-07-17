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


util
----
.. automodule:: drymass.util
    :members:


roi
---
The :class:`ROIManager` class is used to manage and save/load ROI positions.

And the content of "output_rois.txt" is:

.. include:: output_rois.txt
    :literal:

.. automodule:: drymass.roi
    :members:

