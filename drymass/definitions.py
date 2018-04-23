import numpy as np

from .cfg_funcs import fbool, float_or_str, int_or_str, lcstr, \
    floattuple_or_one, tupletupleint


config = {
    "bg": {
        "amplitude data":
            ("none", int_or_str, "Amplitude bg correction file or index"),
            # Image indexing starts with 1.
        "amplitude offset":
            ("mean", lcstr, "Amplitude bg correction offset method"),
            # Valid values are defined in
            # :data:`qpimage.bg_estimate.VALID_FIT_OFFSETS`.
        "amplitude profile":
            ("tilt", lcstr, "Amplitude bg correction profile method"),
            # Valid values are defined in
            # :data:`qpimage.bg_estimate.VALID_FIT_PROFILES`.
        "amplitude binary threshold":
            (np.nan, float_or_str, "Binary image threshold value or method"),
            # If not *nan*, defines either a threshold for background
            # segmentation or a method in :mod:`skimage.filters`.
        "amplitude border perc":
            (10, float, "Amplitude bg border region to analyze [%]"),
        "amplitude border px":
            (5, int, "Amplitude bg border region to analyze [px]"),
        "enabled":
            (True, fbool, "Enable bg correction globally"),
            # Set to *False* when manually editing *roi_slices.txt*.
        "phase data":
            ("none", int_or_str, "Phase bg correction file or index"),
            # Image indexing starts with 1.
        "phase offset":
            ("mean", lcstr, "Phase bg correction offset method"),
            # Valid values are defined in
            # :data:`qpimage.bg_estimate.VALID_FIT_OFFSETS`.
        "phase profile":
            ("tilt", lcstr, "Phase bg correction profile method"),
            # Valid values are defined in
            # :data:`qpimage.bg_estimate.VALID_FIT_PROFILES`.
        "phase binary threshold":
            (np.nan, float_or_str, "Binary image threshold value or method"),
            # If not *nan*, defines either a threshold for background
            # segmentation or a method in :mod:`skimage.filters`.
        "phase border perc":
            (10, float, "Phase bg border region to analyze [%]"),
        "phase border px":
            (5, int, "Phase bg border region to analyze [px]"),
    },
    "holo": {
        "filter name":  # filter_name
            ("disk", str, "Filter name for sideband isolation"),
        "filter size":  # filter_size
            (1/3, float, "Filter size (fraction of the sideband frequency)"),
        "sideband":  # sideband
            (1, floattuple_or_one, "Sideband ±1 or frequency coordinates"),
    },
    "meta": {
        "medium index":
            (np.nan, float, "Refractive index of the surrounding medium"),
        "pixel size um":
            (np.nan, float, "Detector pixel size [µm]"),
        "wavelength nm":
            (np.nan, float, "Imaging wavelength [nm]"),
    },
    "output": {
        "roi images":
            (True, fbool, "Rendered phase images with ROI location"),
        "sphere images":
            (True, fbool, "Phase/Intensity images for sphere analysis"),
        "sensor tif data":
            (True, fbool, "Phase/Amplitude sensor tif data"),
    },
    "roi": {
        "dist border":
            (10, int, "Minimum distance of objects to image border [px]"),
        "eccentricity max":
            (0.7, float, "Allowed maximal eccentricity of the specimen"),
        "enabled":
            (True, fbool, "Perform automated search for ROIs"),
            # If set to *False*, the file "roi_slices.txt" must contain ROIs.
        "exclude overlap":
            (30.0, float, "Allowed distance between two objects [px]"),
        "force":
            ((), tupletupleint, "Force ROI coordinates (x1,x2,y1,y2) [px]"),
        "pad border":
            (40, int, "Padding of object regions [px]"),
        "size variation":
            (0.5, float, "Allowed variation relative to specimen size"),
    },
    "specimen": {
        "size um":
            (10, float, "Approximate diameter of the specimen [µm]"),
            # This is used as the initial value for the sphere analysis.
    },
    "sphere": {
        "edge coarse":
            (0.4, float, "Coarse edge detection filter size"),
        "edge fine":
            (0.1, float, "Fine edge detection filter size"),
        "edge clip radius min":
            (0.9, float, "Interior edge point filtering radius"),
        "edge clip radius max":
            (1.1, float, "Exterior edge point filtering radius"),
        "edge iter":
            (20, int, "Maximum number iterations for coarse edge detection"),
        "image fit range position":  # crel
            (0.05, float, "Fit interpolation range for radius"),
        "image fit range radius":  # rrel
            (0.05, float, "Fit interpolation range for radius"),
        "image fit range refractive index":  # nrel
            (0.10, float, "Fit interpolation range for refractive index"),
        "image fix phase offset":  # fix_pha_offset
            (False, fbool, "Fix the simulation background phase to zero"),
        "image iter":  # max_iter
            (100, int, "Maximum number of iterations for image fitting"),
        "image stop delta position":  # stop_dc
            (1, float, "Stopping criterion for position"),
        "image stop delta radius":  # stop_dr
            (0.0010, float, "Stopping criterion for radius"),
        "image stop delta refractive index":  # stop_dn
            (0.0005, float, "Stopping criterion for refractive index"),
        "image verbosity":  # verbose
            (1, int, "Verbosity level of image fitting algorithm"),
        "method":
            ("edge", lcstr, "Method for determining sphere parameters"),
            # Valid values are *edge* (edge-detection approach) or
            # *image* (2D phase image fitting).
        "model":
            # Valid values are defined in
            # :data:`qpsphere.models.available`. If *method=edge*, then
            # *model* must be set to *projection*. If *method=image*,
            # setting *model* to *rytov-sc* has the best trade-off between
            # accuracy and speed.
            ("projection", lcstr, "Physical sphere model"),
        "refraction increment":
            (0.18, float, "Refraction increment [mL/g]"),
        "radial inclusion factor":
            (1.2, float, "Radial inclusion factor for dry mass computation"),
    },
}
