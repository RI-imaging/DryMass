.. _section_install:

==================
Installing DryMass
==================

DryMass is written in pure Python and supports Python version 3.6
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

If you wish to install a specific version of DryMass (e.g. 0.3.0), use

``pip install 'drymass==0.3.0'``.


Known issues
------------
 - If you try to install from PyPI and get an error message similar to
   
   
   | `"Could not find a version that satisfies the requirement drymass (from versions: )`
   | `No matching distribution found for drymass`",
   
   please make sure that you are using Python version 3.6 or later with ``python --version``.
   If that is already the case, please run ``pip -vvv install drymass`` and create an
   `issue <https://github.com/RI-imaging/DryMass/issues>`_ with the error
   messages (e.g. as a screenshot) that you get.

 - If you are using Windows and the installation fails because `scikit-image` cannot
   be installed, e.g.
 
   | `"  Rolling back uninstall of scikit-image`
   | `Command python.exe [...] --compile failed with error code 1 in [...]/scikit-image`",
   
   and you are using the
   `Anaconda Python distribution <https://www.anaconda.com/download/#windows>`_, please
   install `scikit-image` via ``conda install scikit-image``.
   If you are not using Anaconda, you can install one of the `wheels
   provided by Christoph Gohlke <https://www.lfd.uci.edu/~gohlke/pythonlibs/#scikit-image>`_
   (download e.g. "scikit_image‑0.14.0‑cp36‑cp35m‑win_amd64.whl" if you have installed
   the 64bit version of Python 3.6, navigate to the download directory and run
   ``pip install scikit_image‑0.14.0‑cp35‑cp36m‑win_amd64.whl``). 
