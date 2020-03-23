"""
There are two types of thresholding done in DryMass.

1. Thresholding of the `sensor image` which is required by the
   detection of the phase object ROIs
   (``[roi]: threshold`` configuration parameter)
2. Thresholding of the `individual ROIs` for determining the masked
   area used for ROI background correction
   (``[bg]: amplitude binary threshold``
   and ``[bg]: phase binary threshold`` configuration parameters)
"""
import warnings

import numpy as np
import skimage.filters as skfilters


def image2mask(image, value_or_method, invert=False):
    """Convert an image to a binary mask for background correction

    If `invert` is False, the threshold value is included in the
    resulting array.

    Parameters
    ----------
    image: 2d np.ndarray
        Input image
    value_or_method: float or str
        Either a threshold value or a string naming a
        filter method in :mod:`skimage.filters`.
    invert: bool
        Invert the resulting boolean array
    """
    if isinstance(value_or_method, str):
        if value_or_method.startswith("threshold_"):
            value_or_method = value_or_method[10:]
            warnings.warn("Use of the name of the thresholding function "
                          "from skimage is deprecated. Please use "
                          " '{}' instead!".format(value_or_method),
                          DeprecationWarning)
        method = threshold_dict[value_or_method]
        bw = image >= method(image)
    else:
        bw = image >= value_or_method
    if invert:
        return ~bw
    else:
        return bw


def threshold_drymass_nuclei(image):
    """Threshold filter for segmenting cell nuclei in phase images

    Cell nuclei have a low refractive index, but the nucleoli within
    the nuclei usually have a very high refractive index. As a result,
    conventional thresholding algorithms either cannot detect the
    nuclei reliably or segment the nucleoli only.

    This thresholding filter copes with the situation by
    "pulling down" the top 1% of the phase data and taking the
    threshold at 20% of the maximum phase relative to the mean
    of the original phase data.
    """
    image = image.copy()
    mean = np.mean(image)
    size = image.size
    # ignore the top 1%
    counter = 0
    maxim = np.max(image)
    while counter < size // 100:
        maxid = image == maxim
        counter += np.sum(maxid)
        maxim = np.max(image[~maxid])
        image[maxid] = maxim
    # take 20% as threshold value
    thresh = mean + .2 * (maxim-mean)
    return thresh


def threshold_li(image):
    """Li threshold optimized for cells in QPI"""
    return skfilters.threshold_li(image,
                                  initial_guess=np.percentile(image, q=95))


#: Dictionary containing all thresholding methods available in DryMass
threshold_dict = {
    'dm-nuclei': threshold_drymass_nuclei,
    'isodata': skfilters.threshold_isodata,
    'li': threshold_li,
    'mean': skfilters.threshold_mean,
    'minimum': skfilters.threshold_minimum,
    'otsu': skfilters.threshold_otsu,
    'triangle': skfilters.threshold_triangle,
    'yen': skfilters.threshold_yen,
}

#: Available thresholding method names;
#: The thresholding methods are either defined in this module
#: (see `threshold_*` methods) or taken from :mod:`skimage.filters`.
available_thresholds = sorted(threshold_dict.keys())
