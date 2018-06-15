import os
import tempfile
import shutil

import numpy as np
import pytest
import qpimage

import drymass


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
    with qpimage.QPSeries(h5file=path) as qps:
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
        assert qpso[0]["identifier"].count("sim:projection")

    try:
        os.remove(path)
    except OSError:
        pass
    shutil.rmtree(dout, ignore_errors=True)


@pytest.mark.filterwarnings('ignore::drymass.anasphere.'
                            + 'EdgeDetectionFailedWarning',
                            'ignore::RuntimeWarning')
def test_radius_exceeds_image_size_warning():
    pxsize = 1e-6
    size = 200
    _qpi, path, dout = setup_test_data(pxsize=pxsize, size=size)
    path_out = drymass.analyze_sphere(path, dir_out=dout,
                                      r0=size*pxsize*2)
    with qpimage.QPSeries(h5file=path_out, h5mode="r") as qpso:
        assert np.all(qpso[0].amp == 1)
        assert np.all(qpso[0].pha == 0)

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


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
