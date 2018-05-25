import pathlib
import warnings

import numpy as np
import qpimage
from skimage.external import tifffile
import skimage.filters

from . import search, util
from .roi import ROIManager


# default background correction kwargs
BG_DEFAULT_KW = {"fit_offset": "mean",
                 "fit_profile": "tilt",
                 "border_perc": 5,
                 "border_px": 5,
                 }
# file names
FILE_ROI_DATA_H5 = "roi_data.h5"
FILE_ROI_DATA_TIF = "roi_data.tif"
FILE_SLICES = "roi_slices.txt"


def _extract_roi(h5in, h5out, slout, imout, size_m, size_var, max_ecc,
                 dist_border, pad_border, exclude_overlap, bg_amp_kw,
                 bg_amp_bin, bg_pha_kw, bg_pha_bin, search_enabled):
    # Determine ROI location
    with qpimage.QPSeries(h5file=h5in, h5mode="r") as qps:
        rmgr = ROIManager(qps.identifier)
        if search_enabled:
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
                    slident = "{}.{}".format(qpi["identifier"], jj)
                    rmgr.add(roislice=sl, image_index=ii,
                             roi_index=jj, identifier=slident)
            rmgr.save(slout)
        else:
            rmgr.load(slout)

    # Extract ROI images
    with qpimage.QPSeries(h5file=h5in, h5mode="r") as qps, \
            qpimage.QPSeries(h5file=h5out, h5mode="w") as qps_roi, \
            tifffile.TiffWriter(str(imout), imagej=True) as tf:
        for ii in range(len(qps)):
            # image to analyze
            qpi = qps[ii]
            # available ROIs
            rois = rmgr.get_from_image_index(ii)
            for jj, (rid, sl) in enumerate(rois):
                # Extract the ROI
                qpisl = qpi.__getitem__(sl)
                # amplitude bg correction
                if bg_amp_kw:
                    amp_mask = get_binary(
                        qpisl.amp, value_or_method=bg_amp_bin)
                    qpisl.compute_bg(which_data="amplitude",
                                     from_binary=amp_mask,
                                     **bg_amp_kw)
                # phase bg correction
                if bg_pha_kw:
                    pha_mask = get_binary(
                        qpisl.pha, value_or_method=bg_pha_bin)
                    qpisl.compute_bg(which_data="phase",
                                     from_binary=pha_mask,
                                     **bg_pha_kw)
                slident = "{}.{}".format(qpi["identifier"], jj)
                if rid != slident:
                    # This might happen if the user does not know the
                    # image identifier and builds his own `FILE_SLICES`.
                    msg = "Mismatch of slice and QPImage identifiers: " \
                          + "{} vs {}!".format(rid, slident)
                    warnings.warn(msg)
                    # override `slident` with user identifier
                    slident = rid
                qps_roi.add_qpimage(qpisl, identifier=slident)

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
    return rmgr


def extract_roi(h5series, dir_out, size_m, size_var=.5, max_ecc=.7,
                dist_border=10, pad_border=40, exclude_overlap=30.,
                bg_amp_kw=BG_DEFAULT_KW, bg_amp_bin=np.nan,
                bg_pha_kw=BG_DEFAULT_KW, bg_pha_bin=np.nan,
                search_enabled=True, ret_roimgr=False, ret_changed=False):
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
    search_enabled: bool
        If True, perform automated search for ROIs using the
        parameters above. If False, extract the ROIs from `FILE_SLICES`
        and only perform background correction using the `bg_*`
        parameters.
    ret_roimgr: bool
        Return the ROIManager instance of the found ROIs
    ret_changed: bool
        Return boolean indicating whether the ROI data on disk was
        created/updated (True) or whether previously created ROI
        data was used (False).

    Notes
    -----
    The output hdf5 file `dir_out/FILE_ROI_DATA_H5` is a
    :class:`qpimage.QPSeries` file with the keyword "identifier"
    consisting of two hashes: one from the relevant arguments
    to this method and one from the file `dir_out/FILE_SLICES`.
    This is to ensure that user-manipulated data is taken into
    account when deciding whether the ROIs should be re-computed
    after an initial run.
    """
    h5in = pathlib.Path(h5series)
    dout = pathlib.Path(dir_out)

    h5out = dout / FILE_ROI_DATA_H5
    imout = dout / FILE_ROI_DATA_TIF
    slout = dout / FILE_SLICES

    with qpimage.QPSeries(h5file=h5in, h5mode="r") as qps:
        cfgid = util.hash_object([qps,
                                  size_m,
                                  size_var,
                                  max_ecc,
                                  dist_border,
                                  pad_border,
                                  exclude_overlap,
                                  bg_amp_kw,
                                  bg_amp_bin,
                                  bg_pha_kw,
                                  bg_pha_bin,
                                  search_enabled,
                                  ])

    # Determine whether we have to extract the ROIs
    if h5out.exists() and slout.exists():
        slid = util.hash_file(slout)
        identifier = "{}-{}".format(cfgid, slid)
        with qpimage.QPSeries(h5file=h5out, h5mode="r") as qpo:
            if qpo.identifier == identifier:
                create = False
            else:
                create = True
    else:
        create = True

    if create:
        rmgr = _extract_roi(h5in=h5in,
                            h5out=h5out,
                            slout=slout,
                            imout=imout,
                            size_m=size_m,
                            size_var=size_var,
                            max_ecc=max_ecc,
                            dist_border=dist_border,
                            pad_border=pad_border,
                            exclude_overlap=exclude_overlap,
                            bg_amp_kw=bg_amp_kw,
                            bg_amp_bin=bg_amp_bin,
                            bg_pha_kw=bg_pha_kw,
                            bg_pha_bin=bg_pha_bin,
                            search_enabled=search_enabled,
                            )
        # manually set the identifier with the updated file slout
        slid = util.hash_file(slout)
        identifier = "{}-{}".format(cfgid, slid)
        with qpimage.QPSeries(h5file=h5out, h5mode="a") as qpo:
            qpo.h5.attrs["identifier"] = identifier
    else:
        with qpimage.QPSeries(h5file=h5in, h5mode="r") as qps:
            rmgr = ROIManager(qps.identifier)
        rmgr.load(slout)

    ret = [h5out]
    if ret_roimgr:
        ret.append(rmgr)
    if ret_changed:
        ret.append(create)
    if len(ret) == 1:
        ret = ret[0]
    return ret


def get_binary(image, value_or_method):
    if isinstance(value_or_method, str):
        method = getattr(skimage.filters, value_or_method)
        return image < method(image)
    elif np.isnan(value_or_method):
        return None
    else:
        return image < value_or_method
