import pathlib

import numpy as np
import qpimage
from skimage.external import tifffile
import skimage.filters

from . import search
from .roi import ROIManager


# default background correction kwargs
BG_DEFAULT_KW = {"fit_offset": "mean",
                 "fit_profile": "ramp",
                 "border_perc": 5,
                 "border_px": 5,
                 }
# file names
FILE_ROI_DATA_H5 = "roi_data.h5"
FILE_ROI_DATA_TIF = "roi_data.tif"
FILE_SLICES = "roi_slices.txt"


def extract_roi(h5series, dir_out, size_m, size_var=.5, max_ecc=.7,
                dist_border=10, pad_border=40, exclude_overlap=30.,
                bg_amp_kw=BG_DEFAULT_KW, bg_amp_bin=np.nan,
                bg_pha_kw=BG_DEFAULT_KW, bg_pha_bin=np.nan,
                ret_roimgr=False):
    """Extract ROIs from a qpimage.QPSeries hdf5 file

    Parameters
    ----------
    h5series: str
        Path of qpimage.QPSeries hdf5 file
    dir_out: str
        Path to output directory
    size_m: float
        Approximate diameter of the specimen [m]
    size_var: float
        Allowed variation relative to specimen size
    max_ecc: float
        Allowed maximal eccentricity of the specimen
    dist_border: int
        Minimum distance of objects to image border [px]
    pad_border: int
        Padding of object regions [px]
    exclude_overlap: float
        Allowed distance between two objects [px]
    bg_amp_kw: dict or None
        Amplitude image background correction keyword arguments
        (see :func:`qpimage.QPImage.compute_bg`), defaults
        to `BG_DEFAULT_KW`, set to `None` to disable correction
    bg_amp_bin: float or str
        The amplitude binary threshold value or the method for binary
        threshold determination; see :mod:`skimage.filters`
        `threshold_*` methods
    bg_pha_kw: dict or None
        Phase image background correction keyword arguments
        (see :func:`qpimage.QPImage.compute_bg`), defaults
        to `BG_DEFAULT_KW`, set to `None` to disable correction
    bg_pha_bin: float or str
        The phase binary threshold value or the method for binary
        threshold determination; see :mod:`skimage.filters`
        `threshold_*` methods
    ret_roimgr: bool
        Return the ROIManager instance of the found ROIs
    """
    h5in = pathlib.Path(h5series)
    dout = pathlib.Path(dir_out)

    h5out = dout / FILE_ROI_DATA_H5
    imout = dout / FILE_ROI_DATA_TIF
    slout = dout / FILE_SLICES

    with qpimage.QPSeries(h5file=h5in, h5mode="r") as qps, \
            qpimage.QPSeries(h5file=h5out, h5mode="w") as qps_roi, \
            tifffile.TiffWriter(str(imout), imagej=True) as tf:
        rmgr = ROIManager(qps.identifier)
        for ii in range(len(qps)):
            qpi = qps[ii]
            # find objects
            slices = search.search_phase_objects(
                qpi=qpi,
                size_m=size_m,
                size_var=size_var,
                max_ecc=max_ecc,
                dist_border=dist_border,
                pad_border=pad_border,
                exclude_overlap=exclude_overlap)
            for jj, sl in enumerate(slices):
                # Write QPImage
                qpisl = qpi.__getitem__(sl)
                if bg_amp_kw:
                    amp_mask = get_binary(
                        qpisl.amp, value_or_method=bg_amp_bin)
                    qpisl.compute_bg(which_data="amplitude",
                                     from_binary=amp_mask,
                                     **bg_amp_kw)
                if bg_pha_kw:
                    pha_mask = get_binary(
                        qpisl.pha, value_or_method=bg_pha_bin)
                    qpisl.compute_bg(which_data="phase",
                                     from_binary=pha_mask,
                                     **bg_pha_kw)
                slident = "{}.{}".format(qpi["identifier"], jj)
                qps_roi.add_qpimage(qpisl, identifier=slident)
                rmgr.add(roislice=sl, image_index=ii,
                         roi_index=jj, identifier=slident)

        if len(qps_roi):
            # Write TIF
            # determine largest image
            sxmax = np.max([qq.shape[0] for qq in qps_roi])
            symax = np.max([qq.shape[1] for qq in qps_roi])
            dummy = np.zeros((2, sxmax, symax), dtype=np.float32)
            for qpir in qps_roi:
                dummy[0, :, :] = 0
                dummy[1, :, :] = 1
                res = 1 / qpir["pixel size"] * 1e-6  # use µm
                sx, sy = qpir.shape
                dummy[0, :sx, :sy] = qpir.pha
                dummy[1, :sx, :sy] = qpir.amp
                tf.save(data=dummy, resolution=(res, res, None))

    rmgr.save(slout)
    ret = h5out
    if ret_roimgr:
        ret = ret, rmgr
    return ret


def get_binary(image, value_or_method):
    if isinstance(value_or_method, str):
        method = getattr(skimage.filters, value_or_method)
        return image < method(image)
    elif np.isnan(value_or_method):
        return None
    else:
        return image < value_or_method
