.. _tutorial04:

===================================================
T4: Automating the analysis of large datasets (CLI)
===================================================

Introduction
------------
This tutorial showcases the command-line parameters ``--recursive``
and ``--profile`` (see :ref:`section_cli_advanced`) to automate data
analysis, exemplarily the analysis pipeline of :ref:`tutorial 2 <tutorial02>`.
After this tutorial, you will be able to automate the application of
multiple analysis pipelines with additional, custom analysis steps to
large datasets. 

Prerequisites
-------------
For this tutorial, you need:

- Python 3.6 or above and DryMass version 0.8.0 or above (see :ref:`section_install`)
- Experimental dataset: `DHM_HL60_cells.zip <https://ndownloader.figshare.com/files/17722787>`_ :cite:`MuellerQPIref19`

Setup example measurements
--------------------------
To simulate the presence of several datasets, create a few copies of
``DHM_HL60_cells.zip`` in a designated folder (here ``C:\\Path\to\data\``).
You may also create subfolders and put copies of the dataset there.
The contents of the folder could be three copies:

- ``DHM_HL60_cells_01.zip``
- ``DHM_HL60_cells_02.zip``
- ``DHM_HL60_cells_03.zip``

Create and import analysis profiles
-----------------------------------
In :ref:`tutorial 2 <tutorial02>`, the analysis pipeline is executed
four times with a different ``[sphere]`` section. For each of these
runs, we create a separate profile and import it into the local library
of DryMass so that we may use it later on. The contents of the first
profile are:

.. code::

    [bg]
    phase border px = 30
    phase profile = poly2o

    [meta]
    medium index = 1.335
    pixel size um = 0.107
    wavelength nm = 633.0

    [roi]
    pad border px = 80
    size variation = 0.2
    exclude overlap px = 100
    ignore data = 8.4, 15.2, 18.2, 18.3, 35.2
    
    [specimen]
    size um = 13
    
    [sphere]
    method = edge
    model = projection

The other profiles are identical to the first profile, except
for the ``[sphere]`` section. First, download all profiles: 

- edge-projection: :download:`t04_profile_edge.cfg`
- image-projection: :download:`t04_profile_proj.cfg`
- image-rytov: :download:`t04_profile_rytov.cfg`
- image-rytov-sc: :download:`t04_profile_rytov-sc.cfg`

and then import them into the local library via:

.. code::

    dm_profile add t4edge t04_profile_edge.cfg
    dm_profile add t4proj t04_profile_proj.cfg
    dm_profile add t4rytov t04_profile_rytov.cfg
    dm_profile add t4rytov-sc t04_profile_rytov-sc.cfg

Once imported in the local library, the downloaded profiles may safely
be removed. You can list the available profile with the command
``dm_profile list``, which should yield an output similar to this:

.. code::

    Available profiles:
     - t4edge: C:\\Users\Something\drymass\profile_t4edge.cfg
     - t4proj: C:\\Users\Something\drymass\profile_t4proj.cfg
     - t4rytov-sc: C:\\Users\Something\drymass\profile_t4rytov-sc.cfg
     - t4rytov: C:\\Users\Something\drymass\profile_t4rytov.cfg

Test the analysis pipeline
--------------------------
Before the next level of automation, let us first test the current analysis
pipeline:

.. code::

    dm_analyze_sphere --recursive --profile t4edge "C:\\Path\to\data\"

where ``C:\\Path\to\data\`` is the folder containing the experimental
data which is searched recursively (``--recursive``) and ``t4edge``
is the name of the profile that employs the edge-detection approach
to determine the radius and the refractive index of the cells.
Now, verify that all datasets were detected and that the analysis results
are identical to those of :ref:`tutorial 2 <tutorial02>`. The output of
the above command should be similar to:

.. code::

    DryMass version 0.8.0
    Recursing into directory tree... Done.
    Input 1/3: C:\\Path\to\data\DHM_HL60_cells_01.zip
    Input 2/3: C:\\Path\to\data\DHM_HL60_cells_02.zip
    Input 3/3: C:\\Path\to\data\DHM_HL60_cells_03.zip
    Analyzing dataset 1/3.
    Converting input data... Done.
    Extracting ROIs... Done.
    Plotting detected ROIs... Done
    Performing sphere analysis... Done.
    Plotting sphere images... Done
    Analyzing dataset 2/3.
    Converting input data... Done.
    Extracting ROIs... Done.
    Plotting detected ROIs... Done
    Performing sphere analysis... Done.
    Plotting sphere images... Done
    Analyzing dataset 3/3.
    Converting input data... Done.
    Extracting ROIs... Done.
    Plotting detected ROIs... Done
    Performing sphere analysis... Done.
    Plotting sphere images... Done


Further automation
------------------
In principle, we could now run all commands in succession to obtain the
fitting results for all model functions:

.. code::

    dm_analyze_sphere --recursive --profile t4edge "C:\\Path\to\data\"
    dm_analyze_sphere --recursive --profile t4proj "C:\\Path\to\data\"
    dm_analyze_sphere --recursive --profile t4rytov "C:\\Path\to\data\"
    dm_analyze_sphere --recursive --profile t4rytov-sc "C:\\Path\to\data\"

However, since these commands have a comparatively long running time, it
makes sense to write a script that can run these commands automatically
for a given path.

Windows users can create a command-script, a text file with the ``.cmd``
extension (e.g. ``analysis.cmd``, with the following content:

.. code::

    dm_analyze_sphere --recursive --profile t4edge $1
    dm_analyze_sphere --recursive --profile t4proj $1
    dm_analyze_sphere --recursive --profile t4rytov $1
    dm_analyze_sphere --recursive --profile t4rytov-sc $1

Linux and MacOS users can create a bash script (``analysis.sh``), with
the following content:

.. code::

    #!/bin/bash
    dm_analyze_sphere --recursive --profile t4edge $1
    dm_analyze_sphere --recursive --profile t4proj $1
    dm_analyze_sphere --recursive --profile t4rytov $1
    dm_analyze_sphere --recursive --profile t4rytov-sc $1

To run the full analysis, you now only need to execute a single command:

.. code::

    # Windows users:
    cd "C:\\Path\to\script"
    .\analysis.cmd "C:\\Path\to\data\"

    # Linux/MacOS users:
    cd "/path/to/script"
    bash analysis.sh "C:\\Path\to\data\"

Plotting the method comparison automatically
--------------------------------------------
We would also like to automatically plot the comparison between the
methods, as in :ref:`tutorial 2 <tutorial02>`. To achieve this, we
modify the original python script to accept a path as a command line
argument and store the comparison plot as ``comparison.png`` in
the results directories:

.. literalinclude:: t04_method_comparison.py
    :language: python
    :linenos:

Put this python script (:download:`t04_method_comparison.py`) into the
same folder as your analysis script and add the following line to the
the analysis script:

.. code::

    python t04_method_comparison.py $1

The final analysis script should now look like this:

- Windows: :download:`t04_analysis.cmd`
- Linux/MacOS: :download:`t04_analysis.sh`

This script fully automates the entire analysis from loading raw data
to generating a comparison plot.
