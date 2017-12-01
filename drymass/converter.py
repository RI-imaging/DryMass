import pathlib

import numpy as np
import qpformat
import qpimage
from skimage.external import tifffile


FILE_SENSOR_DATA_H5 = "sensor_data.h5"
FILE_SENSOR_DATA_TIF = "sensor_data.tif"


def convert(path_in, dir_out, bg_path=None, meta_data={}):

    path = pathlib.Path(path_in).resolve()
    dout = pathlib.Path(dir_out).resolve()

    h5out = dout / FILE_SENSOR_DATA_H5
    imout = dout / FILE_SENSOR_DATA_TIF

    ds = qpformat.load_data(path=path,
                            bg_path=bg_path,
                            meta_data=meta_data)

    if h5out.exists():
        with qpimage.QPSeries(h5file=h5out, h5mode="r") as qpsr:
            if ds.identifier == qpsr.identifier:
                create = False
            else:
                create = True
    else:
        create = True

    if create:
        # Write h5 data
        ds.saveh5(h5out)

    if create or not imout.exists():
        # Also write tif data
        h5series2tif(h5in=h5out, tifout=imout)

    return h5out


def h5series2tif(h5in, tifout):
    with qpimage.QPSeries(h5file=h5in, h5mode="r") as qps, \
            tifffile.TiffWriter(str(tifout), imagej=True) as tf:
        for ii in range(len(qps)):
            qpi = qps[ii]
            res = 1 / qpi["pixel size"] * 1e-6  # use µm
            dshape = (1, qpi.shape[0], qpi.shape[1])
            dataa = np.array(qpi.amp, dtype=np.float32).reshape(*dshape)
            datap = np.array(qpi.pha, dtype=np.float32).reshape(*dshape)
            data = np.vstack((datap, dataa))
            tf.save(data=data, resolution=(res, res, None))
