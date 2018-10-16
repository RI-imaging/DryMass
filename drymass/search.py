import numpy as np
from skimage.filters import threshold_li, threshold_local
from skimage.segmentation import clear_border
from skimage.morphology import label
from skimage.measure import regionprops


def approx_bg(data, filter_size=None):
    """Approximate the image background with Gaussian convolution

    Parameters
    ----------
    data: 2d ndarray
        Data from which to compute the background
    size: float
        Approximate size of the objects on the background. The size
        of the Gaussian is heuristically determined with

        .. math::

            \\sigma = 5 \\cdot \\texttt{size}

    Returns
    -------
    Approximate background of `data`.
    """
    if filter_size is None:
        filter_size = np.sum(data.shape) / 6

    a = np.fft.fft2(data)
    x = np.fft.fftfreq(data.shape[0]).reshape(-1, 1)
    y = np.fft.fftfreq(data.shape[1]).reshape(1, -1)

    sigma = 1 / (5 * filter_size)
    gauss = np.exp(-(x**2 + y**2) / (2 * sigma**2))
    gauss /= np.max(gauss)
    b = a * gauss
    bg = np.fft.ifft2(b)
    return bg.real


def search_objects_base(image, size=110, size_var=.5, max_ecc=.7,
                        dist_border=10, verbose=False):
    """Search objects in images

    The wrapper :func:`search_phase_objects` implements
    a more robust (heuristic) way of finding objects.

    Parameters
    ----------
    image: 2d ndarray
        Input image
    size: float
        Approximate diameter of phase objects in pixels
    size_var: float
        Allowed variation in size (relative to `size`) for the detected
        objects
    max_ecc: float in interval [0,1)
        Maximal eccentricity of the objects. The eccentricity of a
        circle is zero. For an ellipse it is defined as

        .. math::

            \\varepsilon=\\sqrt{\\frac{a^2-b^2}{a^2}}
              = \\sqrt{1-\\left(\\frac{b}{a}\\right)^2}
              = f/a.

    dist_border: float
        Minimum distance of detected regions to the borders of the
        image in pixels
    verbose: bool
        If `True`, print information about ignored regions

    Returns
    -------
    rois: list of regionprops
        Found regions

    See Also
    --------
    skimage.filters.threshold_otsu: threshold for finding objects
    skimage.segmentation.clear_border: remove regions at the border
    skimage.morphology.label: identify regions in binary images
    """
    if np.allclose(image, 0, atol=1e-14, rtol=0):
        # phase images are zero
        # no regions can be found
        return []
    if size_var >= 1 or size_var <= 0:
        msg = "Parameter 'size_var' must be in interval (0, 1), " \
              + "got '{}'!".format(size_var)
        raise ValueError(msg)

    # apply local threshold
    block_size = ((3*size) // 2) * 2 + 1  # odd block size
    locthr = threshold_local(image, block_size=block_size)
    image = image - locthr

    # threshold image
    thresh = threshold_li(image)
    bw = image > thresh
    # label image regions
    object_labels = label(bw)

    # remove artifacts connected to image border
    if dist_border:
        clear_border(object_labels,
                     buffer_size=int(dist_border),
                     in_place=True)
    used_regions = []
    # Filter/draw regions
    ignored_regions = []
    for region in regionprops(object_labels):
        ds = size * size_var
        if (region.eccentricity > max_ecc or
            region.equivalent_diameter > size + ds or
                region.equivalent_diameter < size - ds):
            ignored_regions.append(region)
        else:
            used_regions.append(region)
    if verbose and len(ignored_regions) > 0:
        msg = "The following regions were ignored:\n"
        regs = []
        for reg in ignored_regions:
            regs.append(" - size: {: 7.1f}px, eccentricity: {:.1f}".format(
                reg.equivalent_diameter,
                reg.eccentricity
            )
            )
        msg += "\n".join(regs)
        print(msg)
    return used_regions


def search_phase_objects(qpi, size_m, size_var=.5, max_ecc=.7,
                         dist_border=10, pad_border=40,
                         exclude_overlap=30., verbose=False):
    """Search phase objects in quantitative phase images

    Parameters
    ----------
    qpi: qpimage.QPImage
        Quantitative phase data
    size_m: float
        Expected size of the phase objects
    size_var: float
        Allowed variation in size (relative to `size`) for the detected
        objects
    max_ecc: float in interval [0,1)
        Maximal eccentricity of the objects. The eccentricity of a
        circle is zero. For an ellipse it is defined as

        .. math::

            \\varepsilon=\\sqrt{\\frac{a^2-b^2}{a^2}}
              = \\sqrt{1-\\left(\\frac{b}{a}\\right)^2}
              = f/a.

    dist_border: int
        Minimum distance of detected regions to the borders of the
        image in pixels
    pad_border: int
        Pad the regions of all objects
    exclude_overlap: float
        Allowed distance in pixels between two detected regions
        (without `pad_border`)
    verbose: bool
        If `True`, print information about ignored regions

    Returns
    -------
    slices: list of slice

    Notes
    -----
    Description of the heuristic search algorithm:

    1. Search phase objects in `qpi.raw_pha` with a background
       correction computed from the gaussian-filtered image
    2. If no objects were found and `qpi.bg_pha` is nonzero,
       search objects in `qpi.pha`.
    3. Search objects in `qpi.bg_pha` and remove any overlaps
       with the previously obtained regions.

    See Also
    --------
    search_objects_base: underlying search algorithm
    approx_bg: gaussian-filtered background estimation
    """
    kwfind = {"size": size_m / qpi["pixel size"],
              "size_var": size_var,
              "max_ecc": max_ecc,
              "dist_border": dist_border,
              "verbose": verbose,
              }

    phase = qpi.raw_pha
    bgphase = qpi.bg_pha

    # Search for regions
    # First, compute regions with automatic background estimation
    bgphase_est = approx_bg(phase)
    regs = search_objects_base(phase - bgphase_est, **kwfind)
    # If this does not work, try with the provided background
    if len(regs) == 0 and not np.all(bgphase == 0):
        regs = search_objects_base(phase - bgphase, **kwfind)
    # Detect objects in the background image
    if not np.all(bgphase == 0):
        bgphasecorr = bgphase - approx_bg(bgphase)
        bgregs = search_objects_base(bgphasecorr, **kwfind)
    else:
        bgregs = []

    # Filtering
    # Filter regions that overlap with regions in the background
    delregs = []
    for rr in regs:
        for bb in bgregs:
            dst = np.sqrt((rr.centroid[0] - bb.centroid[0])**2 +
                          (rr.centroid[1] - bb.centroid[1])**2
                          )
            olap = (rr.equivalent_diameter + bb.equivalent_diameter) / 2 - dst
            if olap + exclude_overlap > 0 and rr not in delregs:
                delregs.append(rr)
    for dd in delregs:
        regs.remove(dd)
    # Filter regions that overlap with regions in the image
    delregs = []
    for rr in regs:
        for bb in regs:
            if rr == bb:
                continue
            dst = np.sqrt((rr.centroid[0] - bb.centroid[0])**2 +
                          (rr.centroid[1] - bb.centroid[1])**2
                          )
            olap = (rr.equivalent_diameter + bb.equivalent_diameter) / 2 - dst
            if olap + exclude_overlap > 0:
                delregs.append(rr)
    for dd in delregs:
        if dd in regs:  # make sure `dd` is removed only once
            regs.remove(dd)
    # Create slices and pad the region sizes
    slices = []
    for re in regs:
        x1, y1, x2, y2 = re.bbox
        x1 = max(0, x1 - pad_border)
        y1 = max(0, y1 - pad_border)
        x2 = min(qpi.shape[0], x2 + pad_border)
        y2 = min(qpi.shape[1], y2 + pad_border)
        slices.append((slice(x1, x2), slice(y1, y2)))
    return slices
