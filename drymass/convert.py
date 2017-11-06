import pathlib

import numpy as np
import qpformat
import qpimage
from skimage.external import tifffile


FILE_SENSOR_DATA = "sensor_data.h5"
FILE_SENSOR_IMAGE = "sensor_images.tif"


def convert(path_in, path_out, bg_path=None, meta_data={},
            h5out=None, imout=None):

    path = pathlib.Path(path_in).resolve()
    pout = pathlib.Path(path_out).resolve()

    if not h5out:
        h5out = pout / FILE_SENSOR_DATA

    if not imout:
        imout = pout / FILE_SENSOR_IMAGE

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
        # Write data
        with qpimage.QPSeries(h5file=h5out,
                              h5mode="w",
                              identifier=ds.identifier) as qps, \
             tifffile.TiffWriter(str(imout), imagej=True) as tf:
            for ii in range(len(ds)):
                # Get data
                if ds.is_series:
                    qpi = ds.get_qpimage(ii)
                else:
                    qpi = ds.get_qpimage()
                # Write QPImage
                imid = "{}:{}".format(ds.identifier, ii)
                qps.add_qpimage(qpi, identifier=imid)
                # Write TIF
                res = 1 / qpi["pixel size"] * 1e-6  # use µm
                dshape = (1, qpi.shape[0], qpi.shape[1])
                dataa = np.array(qpi.amp, dtype=np.float32).reshape(*dshape)
                datap = np.array(qpi.pha, dtype=np.float32).reshape(*dshape)
                data = np.vstack((datap, dataa))
                tf.save(data=data, resolution=(res, res, None))

    return h5out
