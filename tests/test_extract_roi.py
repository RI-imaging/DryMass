import os
import tempfile

import numpy as np
import qpimage

import drymass


def test_basic():
    size = 200
    x = np.arange(size).reshape(-1, 1)
    y = np.arange(size).reshape(1, -1)
    cx = 80
    cy = 120
    radius = 30
    r = np.sqrt((x - cx)**2 + (y - cy)**2)
    image = (r < radius) * 1.3
    pxsize = 1e-6
    qpi = qpimage.QPImage(data=image,
                          which_data="phase",
                          meta_data={"pixel size": pxsize})
    path = tempfile.mktemp(suffix=".h5", prefix="drymass_test")
    with qpimage.QPSeries(h5file=path) as qps:
        qps.add_qpimage(qpi, identifier="test")

    with qpimage.QPSeries(h5file=path) as qps:
        qps_roi = drymass.extract_roi(qps, size_m=2 * radius * pxsize)
        assert len(qps) == 1
        qpi2 = qps_roi.get_qpimage(0)
        assert qpi != qpi2
        assert qpi.shape != qpi2.shape

    try:
        os.remove(path)
    except OSError:
        pass


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
