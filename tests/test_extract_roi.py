import os
import tempfile
import shutil

import numpy as np
import qpimage

import drymass


def setup_test_data(radius=30, pxsize=1e-6, size=200, num=1, identifier=None,
                    medium_index=1.335, wavelength=550e-9, bg=None):
    x = np.arange(size).reshape(-1, 1)
    y = np.arange(size).reshape(1, -1)
    cx = 80
    cy = 120
    r = np.sqrt((x - cx)**2 + (y - cy)**2)
    image = (r < radius) * 1.3
    if bg is not None:
        image += bg
    qpi = qpimage.QPImage(data=image,
                          which_data="phase",
                          meta_data={"pixel size": pxsize,
                                     "medium index": medium_index,
                                     "wavelength": wavelength})
    path = tempfile.mktemp(suffix=".h5", prefix="drymass_test_roi")
    dout = tempfile.mkdtemp(prefix="drymass_test_roi_")
    with qpimage.QPSeries(h5file=path, identifier=identifier) as qps:
        for ii in range(num):
            qpid = "{}_test_{}".format(identifier, ii)
            qps.add_qpimage(qpi, identifier=qpid)
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


def test_bg_corr_thresh():
    radius = 30
    pxsize = 1e-6
    bg = .3
    qpi, path, dout = setup_test_data(radius=radius, pxsize=pxsize, bg=bg)

    bg_pha_kw = {"fit_offset": "mean",
                 "fit_profile": "tilt",
                 "border_perc": 0,
                 "border_px": 0}
    path_out = drymass.extract_roi(path,
                                   dir_out=dout,
                                   size_m=2*radius*pxsize,
                                   bg_pha_kw=bg_pha_kw,
                                   bg_pha_bin=bg*1.1)
    with qpimage.QPSeries(h5file=path_out, h5mode="r") as qpso:
        assert np.min(qpso[0].pha) == 0
        assert np.allclose(np.max(qpso[0].pha), np.max(qpi.pha) - bg)

    try:
        os.remove(path)
    except OSError:
        pass
    shutil.rmtree(dout, ignore_errors=True)


def test_bg_corr_mask():
    radius = 30
    pxsize = 1e-6
    size = 200
    bg = np.zeros((size, size)) + .1
    bg += np.linspace(-.3, .5, size).reshape(-1, 1)
    _, path, dout = setup_test_data(radius=radius, size=size,
                                    pxsize=pxsize, bg=bg)
    qpiref, p2, d2 = setup_test_data(radius=radius, size=size,
                                     pxsize=pxsize, bg=None)

    bg_pha_kw = {"fit_offset": "mean",
                 "fit_profile": "tilt",
                 "border_perc": 0,
                 "border_px": 0}
    path_out = drymass.extract_roi(path,
                                   dir_out=dout,
                                   size_m=2*radius*pxsize,
                                   bg_pha_kw=bg_pha_kw,
                                   bg_pha_mask_radial_clearance=1.1)
    with qpimage.QPSeries(h5file=path_out, h5mode="r") as qpso:
        assert np.allclose(np.min(qpso[0].pha), 0, atol=4e-9, rtol=0)
        assert np.allclose(np.max(qpso[0].pha), np.max(qpiref.pha),
                           atol=1.1e-7, rtol=0)

    try:
        os.remove(path)
        os.remove(p2)
    except OSError:
        pass
    shutil.rmtree(dout, ignore_errors=True)
    shutil.rmtree(d2, ignore_errors=True)


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


def test_no_search():
    radius = 30
    pxsize = 1e-6
    identifier = "asdkn179"
    _qpi, path, dout = setup_test_data(radius=radius,
                                       pxsize=pxsize,
                                       identifier=identifier)
    _p1, rm1 = drymass.extract_roi(path,
                                   dir_out=dout,
                                   size_m=2*radius*pxsize,
                                   ret_roimgr=True)
    _p2, rm2 = drymass.extract_roi(path,
                                   dir_out=dout,
                                   size_m=2*radius*pxsize,
                                   search_enabled=False,
                                   ret_roimgr=True,)

    assert rm1.rois == rm2.rois
    assert rm1.identifier == identifier
    assert rm2.identifier == identifier

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
