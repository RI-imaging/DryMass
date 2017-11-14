import pathlib

import numpy as np
import qpimage
from skimage.external import tifffile

from . import search
from .roi import ROIManager


FILE_ROI_DATA_H5 = "roi_data.h5"
FILE_ROI_DATA_TIF = "roi_data.tif"
FILE_SLICES = "roi_slices.txt"


def extract_roi(h5series, dir_out, size_m, size_var=.5, max_ecc=.7,
                dist_border=10, pad_border=40, exclude_overlap=30,
                bg_amp_offset="mean", bg_amp_profile="ramp",
                bg_amp_border_px=5, bg_amp_border_perc=5,
                bg_pha_offset="mean", bg_pha_profile="ramp",
                bg_pha_border_px=5, bg_pha_border_perc=5,
                ret_roimgr=False):

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
                qpisl.compute_bg(which_data="amplitude",
                                 fit_offset=bg_amp_offset,
                                 fit_profile=bg_amp_profile,
                                 border_perc=bg_amp_border_perc,
                                 border_px=bg_amp_border_px)
                qpisl.compute_bg(which_data="phase",
                                 fit_offset=bg_pha_offset,
                                 fit_profile=bg_pha_profile,
                                 border_perc=bg_pha_border_perc,
                                 border_px=bg_pha_border_px)
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
