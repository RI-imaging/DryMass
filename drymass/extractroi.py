from os import fspath
import pathlib
import warnings

import numpy as np
import qpimage
import qpsphere
from skimage.external import tifffile
import skimage.filters

from . import search, util
from .roi import ROIManager


#: Default background correction keyword arguments
BG_DEFAULT_KW = {"fit_offset": "mean",
                 "fit_profile": "tilt",
                 "border_perc": 5,
                 "border_px": 5,
                 }
#: Output ROI qpimage.QPSeries data
FILE_ROI_DATA_H5 = "roi_data.h5"
#: Output phase/amplitude TIFF data
FILE_ROI_DATA_TIF = "roi_data.tif"
#: Output slice locations
FILE_SLICES = "roi_slices.txt"


def _bg_correct(qpi, which_data, bg_kw={}, bg_mask_thresh=np.nan,
                bg_mask_sphere_kw={}):
    if bg_kw:
        if isinstance(bg_mask_thresh, str) or not np.isnan(bg_mask_thresh):
            if which_data == "phase":
                image = qpi.pha
            else:
                image = qpi.amp
            mask1 = image2mask(image,
                               value_or_method=bg_mask_thresh)
        else:
            mask1 = None
        if not np.isnan(bg_mask_sphere_kw["radial_clearance"]):  # sphere mask
            mask2 = qpsphere.cnvnc.bg_phase_mask_for_qpi(
                qpi=qpi,
                r0=bg_mask_sphere_kw["r0"],
                method="edge",
                model="projection",
                edgekw=bg_mask_sphere_kw["edgekw"],
                imagekw={},
                radial_clearance=bg_mask_sphere_kw["radial_clearance"])
        else:
            mask2 = None
        # combine masks
        if mask1 is None and mask2 is None:
            mask = None
        elif mask1 is None:
            mask = mask2
        elif mask2 is None:
            mask = mask1
        else:
            mask = np.logical_and(mask1, mask2)
        # perforn actual bg correction
        qpi.compute_bg(which_data=which_data,
                       from_mask=mask,
                       **bg_kw)


def _extract_roi(h5in, h5out, slout, imout, size_m, size_var, max_ecc,
                 dist_border, pad_border, exclude_overlap, ignore_data,
                 bg_amp_kw, bg_amp_bin, bg_amp_mask_sphere_kw,
                 bg_pha_kw, bg_pha_bin, bg_pha_mask_sphere_kw,
                 search_enabled):
    # Determine ROI location
    with qpimage.QPSeries(h5file=h5in, h5mode="r") as qps:
        rmgr = ROIManager(qps.identifier)
        if search_enabled:
            for ii in range(len(qps)):
                # new indexing convention in drymass 0.6.0
                image_index = ii + 1
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
                    # new indexing convention in drymass 0.6.0
                    roi_index = jj + 1
                    slident = "{}.{}".format(qpi["identifier"], roi_index)
                    rmgr.add(roi_slice=sl,
                             image_index=image_index,
                             roi_index=roi_index,
                             identifier=slident)
            rmgr.save(slout)
        else:
            rmgr.load(slout)

    # Verify ignore_data parameter
    if ignore_data:
        bad_ignore = []
        for item in ignore_data:
            if item.count("."):
                roims = rmgr.get_from_image_index(int(item.split(".")[0]))
                roims = ["{}.{}".format(r.image_index,
                                        r.roi_index) for r in roims]
                if item not in roims:
                    bad_ignore.append(item)
            else:
                if not rmgr.get_from_image_index(int(item)):
                    bad_ignore.append(item)
        if bad_ignore:
            msg = "The following ROIs/images are not present but are set in " \
                  + "`ignore_data`: {}".format(", ".join(bad_ignore))
            raise ValueError(msg)

    # Extract ROI images
    with qpimage.QPSeries(h5file=h5in, h5mode="r") as qps, \
            qpimage.QPSeries(h5file=h5out, h5mode="w") as qps_roi, \
            tifffile.TiffWriter(fspath(imout), imagej=True) as tf:
        for ii in range(len(qps)):
            # new indexing convention in drymass 0.6.0
            image_index = ii + 1
            # image to analyze
            qpi = qps[ii]
            # available ROIs
            rois = rmgr.get_from_image_index(image_index)
            for jj, roi in enumerate(rois):
                # new indexing convention in drymass 0.6.0
                roi_index = jj + 1
                if is_ignored_roi(roi=roi, ignore_data=ignore_data):
                    # ignore data
                    continue
                # Extract the ROI
                qpisl = qpi.__getitem__(roi.roi_slice)
                # amplitude bg correction
                _bg_correct(qpi=qpisl,
                            which_data="amplitude",
                            bg_kw=bg_amp_kw,
                            bg_mask_thresh=bg_amp_bin,
                            bg_mask_sphere_kw=bg_amp_mask_sphere_kw)
                # phase bg correction
                _bg_correct(qpi=qpisl,
                            which_data="phase",
                            bg_kw=bg_pha_kw,
                            bg_mask_thresh=bg_pha_bin,
                            bg_mask_sphere_kw=bg_pha_mask_sphere_kw)
                slident = "{}.{}".format(qpi["identifier"], roi_index)
                if roi.identifier != slident:
                    # This might happen if the user does not know the
                    # image identifier and builds his own `FILE_SLICES`.
                    msg = "Mismatch of slice and QPImage identifiers: " \
                          + "{} vs {}!".format(roi.identifier, slident)
                    warnings.warn(msg)
                    # override `slident` with user identifier
                    slident = roi.identifier
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
                tf.save(data=dummy, resolution=(res, res, None), compress=9)
    return rmgr


def extract_roi(h5series, dir_out, size_m, size_var=.5, max_ecc=.7,
                dist_border=10, pad_border=40, exclude_overlap=30.,
                ignore_data=None,
                bg_amp_kw=BG_DEFAULT_KW, bg_amp_bin=np.nan,
                bg_amp_mask_radial_clearance=np.nan,
                bg_pha_kw=BG_DEFAULT_KW, bg_pha_bin=np.nan,
                bg_pha_mask_radial_clearance=np.nan,
                bg_sphere_edge_kw={}, search_enabled=True,
                ret_roimgr=False, ret_changed=False):
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
    ignore_data: list of str
        Identifiers for sensor images or ROIs to be excluded from
        further analysis. These will be labeled in the output
        tiff file and not written to the output qpseries file.
    bg_amp_kw: dict or None
        Amplitude image background correction keyword arguments
        (see :func:`qpimage.QPImage.compute_bg`), defaults
        to `BG_DEFAULT_KW`, set to `None` to disable correction
    bg_amp_bin: float or str
        The amplitude binary threshold value or the method for binary
        threshold determination; see :mod:`skimage.filters`
        `threshold_*` methods
    bg_amp_mask_radial_clearance: float
        If not NaN, use :func:`qpsphere.cnvnc.bg_phase_mask_for_qpi`
        to compute a mask image and use it for amplitude
        background correction.
    bg_pha_kw: dict or None
        Phase image background correction keyword arguments
        (see :func:`qpimage.QPImage.compute_bg`), defaults
        to `BG_DEFAULT_KW`, set to `None` to disable correction
    bg_pha_bin: float or str
        The phase binary threshold value or the method for binary
        threshold determination; see :mod:`skimage.filters`
        `threshold_*` methods
    bg_pha_mask_radial_clearance: float
        If not NaN, use :func:`qpsphere.cnvnc.bg_phase_mask_for_qpi`
        to compute a mask image and use it for phase
        background correction.
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
                                  ignore_data,
                                  bg_amp_kw,
                                  bg_amp_bin,
                                  bg_amp_mask_radial_clearance,
                                  bg_pha_kw,
                                  bg_pha_bin,
                                  bg_pha_mask_radial_clearance,
                                  bg_sphere_edge_kw,
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
        bg_amp_mask_sphere_kw = {
            "r0": size_m / 2,
            "edgekw": bg_sphere_edge_kw,
            "radial_clearance": bg_amp_mask_radial_clearance}
        bg_pha_mask_sphere_kw = {
            "r0": size_m / 2,
            "edgekw": bg_sphere_edge_kw,
            "radial_clearance": bg_pha_mask_radial_clearance}

        rmgr = _extract_roi(
            h5in=h5in,
            h5out=h5out,
            slout=slout,
            imout=imout,
            size_m=size_m,
            size_var=size_var,
            max_ecc=max_ecc,
            dist_border=dist_border,
            pad_border=pad_border,
            exclude_overlap=exclude_overlap,
            ignore_data=ignore_data,
            bg_amp_kw=bg_amp_kw,
            bg_amp_bin=bg_amp_bin,
            bg_amp_mask_sphere_kw=bg_amp_mask_sphere_kw,
            bg_pha_kw=bg_pha_kw,
            bg_pha_bin=bg_pha_bin,
            bg_pha_mask_sphere_kw=bg_pha_mask_sphere_kw,
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


def image2mask(image, value_or_method):
    """Convert an image to a binary mask

    Parameters
    ----------
    image: 2d np.ndarray
        Input image
    value_or_method: float or str
        Either a threshold value or a string naming a
        filter method in :mod:`skimage.filters`.
    """
    if isinstance(value_or_method, str):
        method = getattr(skimage.filters, value_or_method)
        return image < method(image)
    else:
        return image < value_or_method


def is_ignored_roi(roi, ignore_data):
    """Determine whether a specific ROI should be ignored

    Parameters
    ----------
    roi: drymass.roi.ROI
        ROI instance
    ignore_data: list of str
        List of strings of the form "image_index" or
        "image_index.roi_index" that identify ROIs that
        should be ignored. For instance
        ["1.0", "2.1", "3"].
    """
    imid = roi.image_index
    roid = roi.roi_index
    if (ignore_data
        and (str(imid) in ignore_data
             or "{}.{}".format(imid, roid) in ignore_data)):
        return True
    else:
        return False
