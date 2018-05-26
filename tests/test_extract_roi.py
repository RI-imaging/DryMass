import os
import tempfile
import shutil

import numpy as np
import qpimage

import drymass


def setup_test_data(radius=30, pxsize=1e-6, num=1):
    size = 200
    x = np.arange(size).reshape(-1, 1)
    y = np.arange(size).reshape(1, -1)
    cx = 80
    cy = 120
    r = np.sqrt((x - cx)**2 + (y - cy)**2)
    image = (r < radius) * 1.3
    qpi = qpimage.QPImage(data=image,
                          which_data="phase",
                          meta_data={"pixel size": pxsize})
    path = tempfile.mktemp(suffix=".h5", prefix="drymass_test_roi")
    dout = tempfile.mkdtemp(prefix="drymass_test_roi_")
    with qpimage.QPSeries(h5file=path) as qps:
        for _i in range(num):
            qps.add_qpimage(qpi, identifier="test")
    return qpi, path, dout


def test_basic():
    radius = 30
    pxsize = 1e-6
    qpi, path, dout = setup_test_data(radius=radius, pxsize=pxsize)
    path_out = drymass.extract_roi(path,
                                   dir_out=dout,
                                   size_m=2*radius*pxsize)

    with qpimage.QPSeries(h5file=path_out, h5mode="r") as qpso:
        assert len(qpso) == 1
        qpi2 = qpso.get_qpimage(0)
        assert qpi != qpi2
        assert qpi.shape != qpi2.shape

    try:
        os.remove(path)
    except OSError:
        pass
    shutil.rmtree(dout, ignore_errors=True)


def test_ret_changed():
    radius = 30
    pxsize = 1e-6
    _qpi, path, dout = setup_test_data(radius=radius, pxsize=pxsize)
    _p1, ch1 = drymass.extract_roi(path,
                                   dir_out=dout,
                                   size_m=2*radius*pxsize,
                                   ret_changed=True)
    _p2, ch2 = drymass.extract_roi(path,
                                   dir_out=dout,
                                   size_m=2*radius*pxsize,
                                   ret_changed=True)
    assert ch1, "First call should create data on disk"
    assert not ch2, "Second call should reuse data on disk"

    try:
        os.remove(path)
    except OSError:
        pass
    shutil.rmtree(dout, ignore_errors=True)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
