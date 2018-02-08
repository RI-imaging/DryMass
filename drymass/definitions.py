import numpy as np

from .cfg_funcs import fbool, float_or_str, int_or_str, lcstr, \
    floattuple_or_one, tupletupleint


config = {
    "bg": {
        # indexing starts at 1
        "amplitude data":
            ("none", int_or_str, "Amplitude bg correction file or index"),
        # see qpimage library: e.g. fit, gauss, mean, mode
        "amplitude offset":
            ("mean", lcstr, "Amplitude bg correction offset method"),
        # see qpimage library: e.g. tilt, offset
        "amplitude profile":
            ("tilt", lcstr, "Amplitude bg correction profile method"),
        # see skimage.filters.threshold_*
        "amplitude binary threshold":
            (np.nan, float_or_str, "Binary image threshold value or method"),
        "amplitude border perc":
            (10, float, "Amplitude bg border region to analyze [%]"),
        "amplitude border px":
            (5, int, "Amplitude bg border region to analyze [px]"),
        "enabled":
            (True, fbool, "Enable bg correction globally"),
        # indexing starts at 1
        "phase data":
            ("none", int_or_str, "Phase bg correction file or index"),
        # see qpimage library: e.g. fit, gauss, mean, mode
        "phase offset":
            ("mean", lcstr, "Phase bg correction offset method"),
        # see qpimage library: e.g. tilt, offset
        "phase profile":
            ("tilt", lcstr, "Phase bg correction profile method"),
        # see skimage.filters.threshold_*
        "phase binary threshold":
            (np.nan, float_or_str, "Binary image threshold value or method"),
        "phase border perc":
            (10, float, "Phase bg border region to analyze [%]"),
        "phase border px":
            (5, int, "Phase bg border region to analyze [px]"),
    },
    "holo": {
        # see qpimage.holo.get_field
        # filter_name
        "filter name":
            ("disk", str, "Filter name for sideband isolation"),
        # filter_size
        "filter size":
            (1 / 3, float, "Filter size (fraction of the sideband frequency)"),
        # sideband
        "sideband":
            (1, floattuple_or_one, "Sideband +/-1, or frequency coordinates"),
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
            (.7, float, "Allowed maximal eccentricity of the specimen"),
        # If set to false, the file "roi_slices.txt" must contain ROIs
        "enabled":
            (True, fbool, "Perform automated search for ROIs"),
        "exclude overlap":
            (30., float, "Allowed distance between two objects [px]"),
        "force":
            ((), tupletupleint, "Force ROI coordinates (x1,x2,y1,y2) [px]"),
        "pad border":
            (40, int, "Padding of object regions [px]"),
        "size variation":
            (.5, float, "Allowed variation relative to specimen size"),
    },
    "specimen": {
        # this is used as the initial value for the sphere analysis
        "size um":
            (10, float, "Approximate diameter of the specimen [µm]"),
    },
    "sphere": {
        # see qpsphere.edgefit.contour_canny
        "edge coarse":
            (.4, float, "Coarse edge detection filter size"),
        "edge fine":
            (.1, float, "Fine edge detection filter size"),
        "edge clip radius min":
            (.9, float, "Interior edge point filtering radius"),
        "edge clip radius max":
            (1.1, float, "Exterior edge point filtering radius"),
        "edge iter":
            (20, int, "Maximum number iterations for coarse edge detection"),
        # see qpsphere.imagefit.alg.match_phase
        "image fit range position":  # crel
            (.05, float, "Fit interpolation range for radius"),
        "image fit range radius":  # rrel
            (.05, float, "Fit interpolation range for radius"),
        "image fit range refractive index":  # nrel
            (.10, float, "Fit interpolation range for refractive index"),
        "image fix phase offset":  # fix_pha_offset
            (False, fbool, "Fix the simulation background phase to zero"),
        "image iter":  # max_iter
            (100, int, "Maximum number of iterations for image fitting"),
        "image stop delta position":  # stop_dc
            (1, float, "Stopping criterion for position"),
        "image stop delta radius":  # stop_dr
            (.0010, float, "Stopping criterion for radius"),
        "image stop delta refractive index":  # stop_dn
            (.0005, float, "Stopping criterion for refractive index"),
        "image verbosity":  # verbose
            (1, int, "Verbosity level of image fitting algorithm"),
        # see qpsphere.analyze
        "method":
            ("edge", lcstr, "Method for determining sphere parameters"),
        # see qpsphere.models
        "model":
            ("projection", lcstr, "Physical sphere model"),
        "refraction increment":
            (.18, float, "Refraction increment [mL/g]"),
        "radial inclusion factor":
            (1.2, float, "Radial inclusion factor for dry mass computation"),
    },
}
