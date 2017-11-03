import pathlib

import qpformat
import qpimage


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
                              identifier=ds.identifier) as qps:
            for ii in range(len(ds)):
                if ds.is_series:
                    qpi = ds.get_qpimage(ii)
                else:
                    qpi = ds.get_qpimage()
                imid = "{}:{}".format(ds.identifier, ii)
                qps.add_qpimage(qpi, identifier=imid)

        # Write images
        # TODO

    return h5out
