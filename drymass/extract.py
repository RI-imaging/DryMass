import qpformat
import qpimage

from . import search
from .roi import ROIManager


def extract_objects(path, size_m, var_size=.5, max_ecc=.7,
                    dist_border=10, pad_border=20, exclude_overlap=30,
                    h5out=None, ret_roimgr=False):
    ds = qpformat.load_data(path)
    qps = qpimage.QPSeries(h5file=h5out)
    rmgr = ROIManager(ds)
    for ii in range(len(ds)):
        if ds.is_series:
            qpi = ds.get_qpimage(ii)
        else:
            qpi = ds.get_qpimage()
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
            slident = "{}:{}.{}".format(ds.identifier, ii, jj)
            qps.add_qpimage(qpisl, identifier=slident)
            rmgr.add(sl, image_index=ii, roi_index=jj, identifier=slident)
    ret = qps
    if ret_roimgr:
        ret = ret, rmgr
    return ret
