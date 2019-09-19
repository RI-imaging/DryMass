import os
import pathlib
import tempfile
import time
import shutil

import numpy as np
import pytest
import qpimage
import qpsphere

import drymass

from test_extract_roi import setup_test_data as setup_test_data_roi


def setup_test_data(radius_px=30, size=200, pxsize=1e-6, medium_index=1.335,
                    wavelength=550e-9, num=1):
    x = np.arange(size).reshape(-1, 1)
    y = np.arange(size).reshape(1, -1)
    cx = 80
    cy = 120
    r = np.sqrt((x - cx)**2 + (y - cy)**2)
    image = (r < radius_px) * 1.3
    qpi = qpimage.QPImage(data=image,
                          which_data="phase",
                          meta_data={"pixel size": pxsize,
                                     "medium index": medium_index,
                                     "wavelength": wavelength})
    path = tempfile.mktemp(suffix=".h5", prefix="drymass_test_sphere")
    dout = tempfile.mkdtemp(prefix="drymass_test_sphere_")
    identifier = "abcdef:123456:a1b2c3"
    with qpimage.QPSeries(h5file=path, identifier=identifier) as qps:
        for ii in range(num):
            qps.add_qpimage(qpi, identifier="test_{}".format(ii))
    return qpi, path, dout


def test_basic():
    qpi, path, dout = setup_test_data(num=2)
    path_out = drymass.analyze_sphere(path, dir_out=dout)

    with qpimage.QPSeries(h5file=path_out, h5mode="r") as qpso:
        assert qpso[0].shape == qpi.shape
        assert qpso[0]["wavelength"] == qpi["wavelength"]
        assert qpso[0]["pixel size"] == qpi["pixel size"]
        assert qpso[0]["medium index"] == qpi["medium index"]
        assert qpso[0]["identifier"].count("projection")

    try:
        os.remove(path)
    except OSError:
        pass
    shutil.rmtree(dout, ignore_errors=True)


@pytest.mark.filterwarnings('ignore::drymass.anasphere.'
                            + 'EdgeDetectionFailedWarning',
                            'ignore::RuntimeWarning')
def test_radius_exceeds_image_size_error():
    pxsize = 1e-6
    size = 200
    _qpi, path, dout = setup_test_data(pxsize=pxsize, size=size)
    try:
        drymass.analyze_sphere(path, dir_out=dout, r0=size*pxsize*2)
    except qpsphere.edgefit.RadiusExceedsImageSizeError:
        pass
    else:
        assert False

    try:
        os.remove(path)
    except OSError:
        pass
    shutil.rmtree(dout, ignore_errors=True)


def test_recompute_broken_output_path():
    _qpi, path, dout = setup_test_data()
    path_out = drymass.analyze_sphere(path, dir_out=dout)
    # break it
    with path_out.open("w") as fd:
        fd.write("This file is broken intentionally!")
    _p, changed = drymass.analyze_sphere(path, dir_out=dout, ret_changed=True)
    assert changed, "broken file should be recomputed"
    # delete it
    path_out.unlink()
    _p, changed = drymass.analyze_sphere(path, dir_out=dout, ret_changed=True)
    assert changed, "non-existent file should be recomputed"

    try:
        os.remove(path)
    except OSError:
        pass
    shutil.rmtree(dout, ignore_errors=True)


def test_recompute_edge_when_imagekw_changes():
    _qpi, path, dout = setup_test_data()
    drymass.analyze_sphere(path, dir_out=dout, imagekw={"stop_dc": .9})
    _p, changed = drymass.analyze_sphere(path, dir_out=dout,
                                         imagekw={"stop_dc": .9},
                                         ret_changed=True)
    assert not changed, "same arguments"
    _p, changed = drymass.analyze_sphere(path, dir_out=dout,
                                         imagekw={"stop_dc": .8},
                                         ret_changed=True)
    assert not changed, "different imagekw when method is edge"

    try:
        os.remove(path)
    except OSError:
        pass
    shutil.rmtree(dout, ignore_errors=True)


def test_recompute_edge_when_otherkw_changes():
    _qpi, path, dout = setup_test_data()
    drymass.analyze_sphere(path, dir_out=dout,
                           alpha=0.18,
                           edgekw={"clip_rmax": 1.1})
    _p, changed = drymass.analyze_sphere(path, dir_out=dout,
                                         alpha=0.19,
                                         edgekw={"clip_rmax": 1.1},
                                         ret_changed=True)
    assert changed, "change due to other alpha"
    _p, changed = drymass.analyze_sphere(path, dir_out=dout,
                                         alpha=0.19,
                                         edgekw={"clip_rmax": 1.2},
                                         ret_changed=True)
    assert changed, "change due to other edgekw"

    try:
        os.remove(path)
    except OSError:
        pass
    shutil.rmtree(dout, ignore_errors=True)


def test_recompute_reuse():
    cx = 14
    cy = 16
    radius = 7
    size = 30
    pxsize = 1e-6
    _qpi, path, dout = setup_test_data_roi(num=2,
                                           radius=radius,
                                           pxsize=pxsize,
                                           size=size,
                                           cx=cx,
                                           cy=cy)

    # extract ROIs
    roikw = {"size_m": 2*radius*pxsize,
             "dist_border": 0,
             "pad_border": 3}
    path_rois = drymass.extract_roi(path, dir_out=dout, **roikw)
    # perform sphere analysis
    ta0 = time.perf_counter()
    drymass.analyze_sphere(path_rois, dir_out=dout,
                           method="image",
                           model="projection")
    ta1 = time.perf_counter()

    # extract ROIs, ignoring first image
    drymass.extract_roi(path, dir_out=dout, ignore_data=["1"], **roikw)
    # this time it should be very fast
    tb0 = time.perf_counter()
    _out, changed = drymass.analyze_sphere(path_rois, dir_out=dout,
                                           method="image",
                                           model="projection",
                                           ret_changed=True)
    tb1 = time.perf_counter()

    assert changed, "One ROI was removed, thus change"
    # there should still be a marging of .6s
    assert 10 * (tb1 - tb0) < ta1 - ta0

    try:
        os.remove(path)
    except OSError:
        pass
    shutil.rmtree(dout, ignore_errors=True)


def test_recreate_file_sphere_stat():
    _qpi, path, dout = setup_test_data()
    spkw = {"method": "edge",
            "model": "projection"}
    drymass.analyze_sphere(path, dir_out=dout, **spkw)
    stats = (pathlib.Path(dout) /
             drymass.anasphere.FILE_SPHERE_STAT.format(spkw["method"],
                                                       spkw["model"]))
    stats.unlink()
    assert not stats.exists()
    drymass.analyze_sphere(path, dir_out=dout, **spkw)
    assert stats.exists()

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
