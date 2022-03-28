.. _section_install:

==================
Installing DryMass
==================

DryMass is written in pure Python and supports Python version 3.9
and later. DryMass depends on several other scientific Python packages,
including:

 - `numpy <https://docs.scipy.org/doc/numpy/>`_,
 - `scikit-image <http://scikit-image.org/>`_ (segmentation).
 - `qpimage <https://qpimage.readthedocs.io/en/stable/>`_ (phase data manipulation),
 - `qpformat <https://qpimage.readthedocs.io/en/stable/>`_ (file formats),
 - `qpsphere <https://qpimage.readthedocs.io/en/stable/>`_ (refractive index analysis, segmentation),
    

To install DryMass, use one of the following methods
(package dependencies will be installed automatically):
    
* from `PyPI <https://pypi.python.org/pypi/DryMass>`_:
    ``pip install drymass``
* from `sources <https://github.com/RI-imaging/DryMass>`_:
    ``pip install .`` or 
    ``python setup.py install``


Upgrade
-------
If you have installed an older version of DryMass and wish to upgrade
to the latest version, use

``pip uninstall drymass`` followed by

``pip install drymass``.

If you wish to install a specific version of DryMass (e.g. 0.11.0), use

``pip install 'drymass==0.11.0'``.


Known issues
------------
 - If you try to install from PyPI and get an error message similar to
   
   
   | `"Could not find a version that satisfies the requirement drymass (from versions: )`
   | `No matching distribution found for drymass`",
   
   please make sure that you are using Python version 3.9 or later with ``python --version``.
   If that is already the case, please run ``pip -vvv install drymass`` and create an
   `issue <https://github.com/RI-imaging/DryMass/issues>`_ with the error
   messages (e.g. as a screenshot) that you get.
