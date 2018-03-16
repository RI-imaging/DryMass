.. _tutorial02:

============================
T2: HL60 cell analysis (CLI)
============================

Introduction
------------
`HL60 <https://en.wikipedia.org/wiki/HL60>`_ cells in suspension are
inhomogeneous, almost-spherical objects. To estimate an average refractive
index (RI) of an HL60 cell population, the DryMass command
:ref:`section_dm_analyze_sphere` can be used. This tutorial reproduces
data presented in figure 5d of reference :cite:`Mueller2018`.

Prerequisites
-------------
For this tutorial, you need:

- Python 3.5 or above and DryMass version 0.1.4 or above (see :ref:`section_install`)
- `Fiji <https://fiji.sc/>`_ or Windows Photo Viewer (for data visualization)
- Experimental data set: `DHM_HL60_cells.zip <https://github.com/RI-imaging/QPI-data/raw/master/DHM_HL60_cells.zip>`_

Find regions of interest
------------------------

.. note::

  You can skip this part by copying *roi_slices.txt* from *DHM_HL60_cells.zip*
  into the *DHM_HL60_cells.zip_dm* folder and setting ``enabled = False``
  in the ``[roi]`` section of *drymass.cfg*.
   
We proceed slightly different than in :ref:`tutorial 1<tutorial01>`. Before
we use the command  :ref:`section_dm_analyze_sphere` to extract the RI
values of the HL60 cells, we have to modify our configuration.
We start by executing ``dm_extract_roi DHM_HL60_cells.zip`` which prompts
us for the *pixel size* (0.107µm), and the *wavelength* (633nm),
which can be found in the *readme.txt* file inside the zip archive.

This command imports the raw data and searches for cells in the phase
data. Opening the file *sensor_roi_images.tif*, we realize that the search
parameters are not set correctly. This is image 27:

.. figure:: t02_roi_search1.jpg

We want to exclude small ROIs and ROIs with a large overlap. Furthermore,
we want to include the large cells (image 39). Thus, we change the following
configuration keys in *drymass.cfg*:

.. code-block:: none

  [specimen]
  size = 13              # approximate cell diameter we are looking for [µm]

  [roi]
  pad border = 80        # increase border size around cells
  size variation = 0.2   # do not allow large variations of specimen size
  exclude overlap = 100  # exclude ROIs with an overlap > 100px

With the new configuration, we run ``dm_extract_roi DHM_HL60_cells.zip`` again.
Now all cells are detected. However, we want to exclude a few due to artifacts
or shape issues. To achieve that, we disable the automatic search for ROIs
in *drymass.cfg*

.. code-block:: none

  [roi]
  enabled = False        # use existing roi_slices.txt

and remove the undesired ROIs from *roi_slices.txt*, which are
*7.3, 14.1, 17.1,* and *17.2*. There should now be a total of 88 ROIs.


Set 2nd order polynomial background correction
----------------------------------------------
The default setting for background correction in DryMass is *tilt* which
means that all phase data are corrected by fitting a 2D tilt image to the
image borders. For the present dataset, a second order polynomial fit is
a better approach, because the background phase does not follow a linear
trend. Thus, we choose the *poly2o* profile and additionally set the fitting
border width to 30 pixels. These are the updated lines in the
``[bg]`` section of *drymass.cfg*:

.. code-block:: none

  [bg]
  phase border px = 30
  phase profile = poly2o

Perform sphere analysis
-----------------------
We now run ``dm_analyze_sphere DHM_HL60_cells.zip`` and are asked to enter
the RI of the medium (1.335). By default, the RI of the cells is computed
according to :cite:`Schuermann2015`. The following files are created during
this step:

- *sphere_edge_projection_data.h5*: QPI data
- *sphere_edge_projection_images.tif*: data visualization
- *sphere_edge_projection_statistics.txt*: results

.. note::

    Warnings about *slice and QPImage identifiers* can be safely ignored.
    Setting the RI of the medium changes the internal ROI identifiers.
    Since we have fixed the ROIs, the identifiers do not match anymore,
    but the enumeration is still correct.

Let's have a look at the visualization of ROI 23.0 in
*sphere_edge_projection_images.tif*. 

.. figure:: t02_edge_projection.jpg

The first column shows the experimental data, the second column shows
the modeled data (with the cell perimeter indicated by a dashed circle),
and the third column contains a residual image (pay attention to the colorbar,
green means that the values are outside of the displayed range) and a
line plot through the center of the cell. What is most striking about these
data is that the RI is overestimated while the radius is underestimated
by the edge-projection model.
The explanation is that the radius of the cell is determined with an
edge-detection algorithm applied to the phase image. Since the
edge-detection algorithm determines the edge on the slope of the phase
profile (not where the phase profile starts to deviate from the background),
it underestimates the radius. The solution is to take into account the
full phase image when determining RI and radius :cite:`Kemper2007`
:cite:`Mueller2018`.

In figure 5d of reference :cite:`Mueller2018`, several sphere models are
applied to obtain RI values for the same cell population. To compute these
data, we run ``dm_analyze_sphere DHM_HL60_cells.zip`` three more times
with a modified ``[sphere]`` section (note that this may take a while).

- Run 1: phase image fit with a projection model
  
  .. code-block:: none
  
    [sphere]
    method = image
    model = projection

  which produces the files
  
  - *sphere_image_projection_data.h5*
  - *sphere_image_projection_images.tif*
  - *sphere_image_projection_statistics.txt*

- Run 2: phase image fit with the Rytov approximation
  
  .. code-block:: none
  
    [sphere]
    method = image
    model = rytov

  which produces the files
  
  - *sphere_image_rytov_data.h5*
  - *sphere_image_rytov_images.tif*
  - *sphere_image_rytov_statistics.txt*


- Run 3: phase image fit with the systematically corrected Rytov approximation
  
  .. code-block:: none
  
    [sphere]
    method = image
    model = rytov-sc

  which produces the files
  
  - *sphere_image_rytov-sc_data.h5*
  - *sphere_image_rytov-sc_images.tif*
  - *sphere_image_rytov-sc_statistics.txt*

To verify that the full-phase-image-based approaches indeed yield lower
residuals than the edge-detection approach, let's have a look at ROI 23.0
of *sphere_image_rytov-sc_images.tif*.

.. figure:: t02_image_rytov-sc.jpg
 
The phase difference and the phase line plots look much better now. Observed
deviations mostly originate from the inhomogeneity of the cell.


Plot the results
----------------
To plot the results, we use the following Python program.

.. code:: python

    import matplotlib.pylab as plt
    import numpy as np
    
    def dot_boxplot(ax, data, colors, labels, **kwargs):
        """Boxplot with all data points"""
        box_list = []
    
        for ii in range(len(data)):
            # Set random state
            rs = np.random.RandomState(42).get_state()
            np.random.set_state(rs)
            y = data[ii]
            x = np.random.normal(ii+1, 0.1, len(y))
            plt.plot(x, y, 'o', alpha=0.5, color=colors[ii])
            box_list.append(y)
    
        ax.boxplot(box_list,
                   sym="",
                   medianprops={"color":"black", "linestyle":"solid"},
                   widths=0.3,
                   labels=labels,
                   **kwargs)
        plt.grid(axis="y")

        ri_data = [
            np.loadtxt("sphere_image_rytov-sc_statistics.txt", usecols=(1,)),
            np.loadtxt("sphere_image_rytov_statistics.txt", usecols=(1,)),
            np.loadtxt("sphere_image_projection_statistics.txt", usecols=(1,)),
            np.loadtxt("sphere_edge_projection_statistics.txt", usecols=(1,)),
            ]
        colors = ["#E48620", "#DE2400", "#6e559d", "#048E00"]
        labels = ["Ryt-SC", "Rytov", "OPD-pj", "OPD-ed"]    
    
        plt.figure(figsize=(8,8))
        ax = plt.subplot(111)
        dot_boxplot(ax=ax, data=ri_data, colors=colors, labels=labels)
        plt.tight_layout()
        plt.show()

.. figure:: t02_reproduced_5d.jpg
