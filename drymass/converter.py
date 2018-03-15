import numbers
import pathlib

import numpy as np
import qpformat
import qpimage
from skimage.external import tifffile


FILE_SENSOR_DATA_H5 = "sensor_data.h5"
FILE_SENSOR_DATA_TIF = "sensor_data.tif"


def convert(path_in, dir_out, meta_data={}, holo_kw={},
            bg_data_amp=None, bg_data_pha=None,
            write_tif=False, ret_dataset=False):
    """Convert experimental data to `qpimage.QPSeries` on disk

    Parameters
    ----------
    bg_data_amp, bg_data_pha: None, int, or path to file
        The background data for phase and amplitude. One of

        - `None`:
          No background data
        - `int`:
          Image index (starting at 1) of the input data set
          to use as background data
        - `str`, `pathlib.Path`:
          Path to a separate file that is used for background
          correction, relative to the directory in which `path_in`
          is located (`path_in.parent`).
    """
    path = pathlib.Path(path_in).resolve()
    dout = pathlib.Path(dir_out).resolve()

    h5out = dout / FILE_SENSOR_DATA_H5
    imout = dout / FILE_SENSOR_DATA_TIF

    ds = qpformat.load_data(path=path, meta_data=meta_data, holo_kw=holo_kw)

    if not (bg_data_amp is None and bg_data_pha is None):
        # Only set background of data set if there is
        # a background defined.
        if bg_data_amp is None:
            bgamp = np.ones(ds.get_qpimage(0).shape)
        elif isinstance(bg_data_amp, numbers.Integral):
            if bg_data_amp <= 0 or bg_data_amp > len(ds):
                msg = "Amplitude background index must be between 1 and " \
                      + "{}".format(len(ds))
                raise ValueError(msg)
            # indexing in configuration file starts at 1
            bgamp = ds.get_qpimage(bg_data_amp - 1).amp
        elif isinstance(bg_data_amp, (str, pathlib.Path)):
            bgamppath = path_in.parent / bg_data_amp
            dsbgamp = qpformat.load_data(path=bgamppath, meta_data=meta_data)
            if len(dsbgamp) != 1:
                msg = "Background correction with series data not implemented!"
                raise NotImplementedError(msg)
            else:
                bgamp = dsbgamp.get_qpimage(0).amp
        else:
            raise ValueError("Undefined bg_data_amp: {}".format(bg_data_amp))

        if bg_data_pha is None:
            bgpha = np.zeros(ds.get_qpimage(0).shape)
        elif isinstance(bg_data_amp, numbers.Integral):
            if bg_data_pha <= 0 or bg_data_pha > len(ds):
                msg = "Phase data index must be between 1 and {}".format(
                    len(ds))
                raise ValueError(msg)
            # indexing in configuration file starts at 1
            bgpha = ds.get_qpimage(bg_data_pha - 1).pha
        elif isinstance(bg_data_pha, (str, pathlib.Path)):
            bgphapath = path_in.parent / bg_data_amp
            dsbgpha = qpformat.load_data(path=bgphapath, meta_data=meta_data)
            if len(dsbgpha) != 1:
                msg = "Background correction with series data not implemented!"
                raise NotImplementedError(msg)
            else:
                bgpha = dsbgpha.get_qpimage(0).pha
        else:
            raise ValueError("Undefined bg_data_pha: {}".format(bg_data_pha))

        bg_data = qpimage.QPImage(data=(bgpha, bgamp),
                                  which_data=("phase", "amplitude"))
        ds.set_bg(bg_data)

    if h5out.exists():
        with qpimage.QPSeries(h5file=h5out, h5mode="r") as qpsr:
            if (ds.identifier == qpsr.identifier and
                    len(ds) == len(qpsr)):
                # file has same identifier and same number of qpimages
                create = False
            else:
                create = True
    else:
        create = True

    if create:
        # Write h5 data
        ds.saveh5(h5out)

    if write_tif and (create or not imout.exists()):
        # Also write tif data
        h5series2tif(h5in=h5out, tifout=imout)

    if ret_dataset:
        return h5out, ds
    else:
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
