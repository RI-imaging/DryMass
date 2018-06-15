import numbers
import pathlib

import numpy as np
import qpformat
import qpimage
from skimage.external import tifffile


FILE_SENSOR_DATA_H5 = "sensor_data.h5"
FILE_SENSOR_DATA_TIF = "sensor_data.tif"


def convert(path_in, dir_out, meta_data={}, holo_kw={},
            bg_data_amp=None, bg_data_pha=None, write_tif=False,
            ret_dataset=False, ret_changed=False):
    """Convert experimental data to `qpimage.QPSeries` on disk

    Parameters
    ----------
    bg_data_amp, bg_data_pha: None, int, or path to file
        The background data for phase and amplitude. One of

        - `None`:
          No background data
        - `int`:
          Image index (starting at 0) of the input data set
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
        bgamp = get_background(bg_data=bg_data_amp,
                               dataset=ds,
                               which="amplitude")
        bgpha = get_background(bg_data=bg_data_pha,
                               dataset=ds,
                               which="phase")
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

    ret = [h5out]
    if ret_dataset:
        ret.append(ds)
    if ret_changed:
        ret.append(create)
    if len(ret) == 1:
        ret = ret[0]
    return ret


def get_background(bg_data, dataset, which="phase"):
    """Obtain the background data for a dataset

    Parameters
    ----------
    bg_data: None, int, str, or pathlib.Path
        Represents the background data:

        - None: no background data
        - int: image with this index in `dataset` is used
          for background correction
        - str, pathlib.Path: An external file will be used for background
          correction.
    dataset: qpformat.dataset.SeriesData
        The dataset for which the background data is collected.
        No background correction is performed! `dataset` is needed
        for integer `bg_data` and for path-based `bg_data`
        (because of meta data and hologram kwargs).

    Returns
    -------
    bg: 2d np.ndarray
        The background data.
    """
    if which not in ["phase", "amplitude"]:
        raise ValueError("`which` must be 'phase' or 'amplitude'!")
    if bg_data is None:
        bg = np.ones(dataset.get_qpimage(0).shape)
    elif isinstance(bg_data, numbers.Integral):
        if bg_data < 0 or bg_data > (len(dataset)-1):
            msg = "Background {} index must be between 0 and {}!"
            raise ValueError(msg.format(which, len(dataset)-1))
        # indexing in configuration file starts at 0
        if which == "phase":
            bg = dataset.get_qpimage(bg_data).pha
        else:
            bg = dataset.get_qpimage(bg_data).amp
    elif isinstance(bg_data, (str, pathlib.Path)):
        bgpath = pathlib.Path(bg_data)
        dsbg = qpformat.load_data(path=bgpath,
                                  meta_data=dataset.meta_data,
                                  holo_kw=dataset.holo_kw)
        if len(dsbg) != 1:
            msg = "Background correction with series data not implemented!"
            raise NotImplementedError(msg)
        else:
            if which == "phase":
                bg = dsbg.get_qpimage(0).pha
            else:
                bg = dsbg.get_qpimage(0).amp
    else:
        msg = "Unknown type for {} `bg_data`: {}".format(which, bg_data)
        raise ValueError(msg)
    return bg


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
