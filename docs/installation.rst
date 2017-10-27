Installing DryMass
===================

DryMass is written in pure Python and supports Python version 3.5
and higher. DryMass depends on several other scientific Python packages,
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
