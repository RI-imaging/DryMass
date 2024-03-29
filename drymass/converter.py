import numbers
from os import fspath
import pathlib
import warnings

import appdirs
import numpy as np
import pyfftw
import qpformat
import qpimage
import tifffile

from . import util

#: Output qpimage.QPSeries sensor data
FILE_SENSOR_DATA_H5 = "sensor_data.h5"
#: Output phase/amplitude TIFF sensor data
FILE_SENSOR_DATA_TIF = "sensor_data.tif"

CACHE_DIR = pathlib.Path(appdirs.user_cache_dir(appname="drymass"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)
PYFFTW_WIDOM_PATH = CACHE_DIR / "pyfftw.wisdom"

if PYFFTW_WIDOM_PATH.exists():
    pyfftw.import_wisdom(
        [w.encode() for w in PYFFTW_WIDOM_PATH.read_text().split("\t")])


def convert(path_in, dir_out, meta_data=None, holo_kw=None, qpretrieve_kw=None,
            bg_data_amp=None, bg_data_pha=None, write_tif=False,
            ret_dataset=False, ret_changed=False, count=None, max_count=None):
    """Convert experimental data to `qpimage.QPSeries` on disk

    Parameters
    ----------
    path_in: str or pathlib.Path
        Input path to file or directory
    dir_out: str or pathlib.Path
        Outuput direcory
    meta_data: dict
        Metadata (see `qpimage.meta.META_KEYS`)
    qpretrieve_kw: dict
        Keyword arguments passed to
        :ref:`qpretrieve <qpretrieve:index>` for
        phase retrieval from interferometric data.
    holo_kw: dict
        This is deprecated, please use `qpretrieve_kw` instead.
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
    write_tif: bool
        Export tif images for use with Fiji/ImageJ (tif images
        are only created if they don't already exist or if the
        analysis changed)
    ret_dataset: bool
        Return the qpformat dataset
    ret_changed: bool
        Return True if the dataset changed
    count, max_count: multiprocessing.Value
        Can be used to monitor the progress of the algorithm.
        Initially, the value of `max_count.value` is incremented
        by the total number of steps. At each step, the value
        of `count.value` is incremented.
    """
    path = pathlib.Path(path_in).resolve()
    dout = pathlib.Path(dir_out).resolve()

    h5out = dout / FILE_SENSOR_DATA_H5
    imout = dout / FILE_SENSOR_DATA_TIF

    ds = qpformat.load_data(path=path,
                            meta_data=meta_data,
                            holo_kw=holo_kw,
                            qpretrieve_kw=qpretrieve_kw)

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

    if util.is_series_file(h5out):
        with qpimage.QPSeries(h5file=h5out, h5mode="r") as qpsr:
            if (ds.identifier == qpsr.identifier and
                    len(ds) == len(qpsr)):
                # file has same identifier and same number of QPSeries
                create = False
            else:
                create = True
    else:
        create = True

    tif_count = max(1, len(ds)//10)
    if max_count is not None:
        with max_count.get_lock():
            max_count.value += len(ds)
            max_count.value += tif_count

    if create:
        # Write h5 data
        ds.saveh5(h5out, count=count)
    else:
        if count is not None:
            with count.get_lock():
                count.value += len(ds)

    if write_tif and (create or not imout.exists()):
        # Also write tif data
        h5series2tif(h5in=h5out, tifout=imout)
    if count is not None:
        with count.get_lock():
            count.value += tif_count

    ret = [h5out]
    if ret_dataset:
        ret.append(ds)
    if ret_changed:
        ret.append(create)
    if len(ret) == 1:
        ret = ret[0]

    PYFFTW_WIDOM_PATH.write_text(
        "\t".join([w.decode() for w in pyfftw.export_wisdom()]))

    return ret


def get_background(bg_data, dataset, which="phase"):
    """Obtain the background data for a dataset

    Parameters
    ----------
    bg_data: None, int, str, or pathlib.Path
        Represents the background data:

        - None: no background data
        - int: image with index `bg_data - 1` in `dataset` is used
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
        if bg_data < 1 or bg_data > len(dataset):
            msg = "Background {} index must be between 1 and {}!"
            raise ValueError(msg.format(which, len(dataset)))
        # indexing in configuration file starts at 1
        if which == "phase":
            bg = dataset.get_qpimage(bg_data - 1).pha
        else:
            bg = dataset.get_qpimage(bg_data - 1).amp
    elif isinstance(bg_data, (str, pathlib.Path)):
        bgpath = pathlib.Path(bg_data)
        dsbg = qpformat.load_data(path=bgpath,
                                  meta_data=dataset.meta_data,
                                  qpretrieve_kw=dataset.qpretrieve_kw)
        if len(dsbg) != 1:
            warnings.warn(
                "Background correction with series data not implemented, "
                + "using first image")
        if which == "phase":
            bg = dsbg.get_qpimage(0).pha
        else:
            bg = dsbg.get_qpimage(0).amp
    else:
        msg = "Unknown type for {} `bg_data`: {}".format(which, bg_data)
        raise ValueError(msg)
    return bg


def h5series2tif(h5in, tifout):
    """Convert a qpimage.QPSeries file to a phase/amplitude TIFF file"""
    with qpimage.QPSeries(h5file=h5in, h5mode="r") as qps, \
            tifffile.TiffWriter(fspath(tifout), imagej=True) as tf:
        for ii in range(len(qps)):
            qpi = qps[ii]
            res = 1 / qpi["pixel size"] * 1e-6  # use µm
            dshape = (1, qpi.shape[0], qpi.shape[1])
            dataa = np.array(qpi.amp, dtype=np.float32).reshape(*dshape)
            datap = np.array(qpi.pha, dtype=np.float32).reshape(*dshape)
            data = np.vstack((datap, dataa))
            tf.save(data=data,
                    resolution=(res, res, None),
                    compress=0,
                    )
