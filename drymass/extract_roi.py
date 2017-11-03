import qpimage

from . import search
from .roi import ROIManager


def extract_roi(qps, size_m, var_size=.5, max_ecc=.7,
                dist_border=10, pad_border=20, exclude_overlap=30,
                h5out=None, ret_roimgr=False):
    rmgr = ROIManager(qps)
    qps_roi = qpimage.QPSeries(h5file=h5out, h5mode="w")
    for ii in range(len(qps)):
        qpi = qps[ii]
        # find objects
        slices = search.search_phase_objects(qpi=qpi,
                                             size_m=size_m,
                                             var_size=var_size,
                                             max_ecc=max_ecc,
                                             dist_border=dist_border,
                                             pad_border=pad_border,
                                             exclude_overlap=exclude_overlap)
        for jj, sl in enumerate(slices):
            qpisl = qpi.__getitem__(sl)
            slident = "{}.{}".format(qpi["identifier"], jj)
            qps_roi .add_qpimage(qpisl, identifier=slident)
            rmgr.add(sl, image_index=ii, roi_index=jj, identifier=slident)
    ret = qps_roi
    if ret_roimgr:
        ret = ret, rmgr
    return ret
