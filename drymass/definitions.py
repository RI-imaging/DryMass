import numpy as np

from .cfg_funcs import fbool, float_or_str, int_or_str, lcstr, tupletupleint


config = {
    "bg": {
        # indexing starts at 1
        "amplitude data":
            ("none", int_or_str, "Amplitude bg correction file or index"),
        # see qpimage library: e.g. fit, gauss, mean, mode
        "amplitude offset":
            ("mean", lcstr, "Amplitude bg correction offset method"),
        # see qpimage library: e.g. ramp, offset
        "amplitude profile":
            ("ramp", lcstr, "Amplitude bg correction profile method"),
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
        # see qpimage library: e.g. ramp, offset
        "phase profile":
            ("ramp", lcstr, "Phase bg correction profile method"),
        # see skimage.filters.threshold_*
        "phase binary threshold":
            (np.nan, float_or_str, "Binary image threshold value or method"),
        "phase border perc":
            (10, float, "Phase bg border region to analyze [%]"),
        "phase border px":
            (5, int, "Phase bg border region to analyze [px]"),
    },
    "roi": {
        "dist border":
            (10, int, "Minimum distance of objects to image border [px]"),
        "eccentricity max":
            (.7, float, "Allowed maximal eccentricity of the specimen"),
        "exclude overlap":
            (30., float, "Allowed distance between two objects [px]"),
        "force":
            ((), tupletupleint, "Force ROI coordinates (x1,x2,y1,y2) [px]"),
        "pad border":
            (40, int, "Padding of object regions [px]"),
        "size variation":
            (.5, float, "Allowed variation relative to specimen size"),
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
    "specimen": {
        "size um":
            (10, float, "Approximate diameter of the specimen [µm]"),
    },
    "sphere": {
        "method":
            ("edge", lcstr, "Method for determining sphere parameters"),
        "model":
            ("projection", lcstr, "Physical sphere model"),
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
        "refraction increment":
            (.18, float, "Refraction increment [mL/g]"),
        "radial inclusion factor":
            (1.2, float, "Radial inclusion factor for dry mass computation"),
    },
}
