import os
import tempfile
import shutil

import numpy as np
import qpimage

import drymass


def setup_test_data(radius_px=30, size=200, pxsize=1e-6, medium_index=1.335,
                    wavelength=550e-9, num=1):
    x = np.arange(size).reshape(-1, 1)
    y = np.arange(size).reshape(1, -1)
    cx = 80
    cy = 120
    r = np.sqrt((x - cx)**2 + (y - cy)**2)
    pha = (r < radius_px) * 1.3
    amp = .5 + np.roll(pha, 10) / pha.max()
    qpi = qpimage.QPImage(data=(pha, amp),
                          which_data="phase,amplitude",
                          meta_data={"pixel size": pxsize,
                                     "medium index": medium_index,
                                     "wavelength": wavelength})
    path = tempfile.mktemp(suffix=".h5", prefix="drymass_test_convert")
    dout = tempfile.mkdtemp(prefix="drymass_test_sphere_")
    with qpimage.QPSeries(h5file=path, h5mode="w") as qps:
        for ii in range(num):
            qps.add_qpimage(qpi, identifier="test_{}".format(ii))
    return qpi, path, dout


def test_bg_correction_index():
    qpi, path, dout = setup_test_data(num=2)

    path_out = drymass.convert(path_in=path,
                               dir_out=dout,
                               bg_data_amp=1,
                               bg_data_pha=1)
    with qpimage.QPSeries(h5file=path_out, h5mode="r") as qps:
        # background correction with same input image will result
        # in a flat QPImage.
        assert np.all(qps[0].pha == 0)
        assert np.all(qps[0].amp == 1)

    # To be absolutely sure this works, append a blank
    # QPImage and do it again.
    with qpimage.QPSeries(h5file=path, h5mode="a") as qps:
        pha = .5 * np.ones(qps[0].shape)
        amp = .9 * np.ones(qps[0].shape)
        qps.add_qpimage(qpimage.QPImage(data=(pha, amp),
                                        which_data="phase,amplitude"))

    path_out = drymass.convert(path_in=path,
                               dir_out=dout,
                               bg_data_amp=3,
                               bg_data_pha=3)
    with qpimage.QPSeries(h5file=path_out, h5mode="r") as qps:
        # background correction with same input image will result
        # in a flat QPImage.
        assert np.allclose(qps[0].pha, qpi.pha - .5)
        assert np.allclose(qps[0].amp, qpi.amp / .9)

    try:
        os.remove(path)
    except OSError:
        pass
    shutil.rmtree(dout, ignore_errors=True)


def test_bg_correction_index_bad():
    _qpi, path, dout = setup_test_data(num=2)

    try:
        drymass.convert(path_in=path, dir_out=dout, bg_data_amp=0)
    except ValueError:
        pass
    else:
        assert False

    try:
        drymass.convert(path_in=path, dir_out=dout, bg_data_pha=-1)
    except ValueError:
        pass
    else:
        assert False

    try:
        drymass.convert(path_in=path, dir_out=dout, bg_data_amp=3)
    except ValueError:
        pass
    else:
        assert False

    try:
        drymass.convert(path_in=path, dir_out=dout, bg_data_pha=3)
    except ValueError:
        pass
    else:
        assert False

    try:
        os.remove(path)
    except OSError:
        pass
    shutil.rmtree(dout, ignore_errors=True)


def test_bg_correction_invalid():
    _qpi, path, dout = setup_test_data(num=2)

    try:
        drymass.convert(path_in=path, dir_out=dout, bg_data_pha=np.zeros(10))
    except ValueError:
        pass
    else:
        assert False

    try:
        drymass.convert(path_in=path, dir_out=dout, bg_data_pha=1.2)
    except ValueError:
        pass
    else:
        assert False

    try:
        os.remove(path)
    except OSError:
        pass
    shutil.rmtree(dout, ignore_errors=True)


def test_bg_correction_none_bad():
    _qpi, path, dout = setup_test_data(num=2)

    path_out = drymass.convert(path_in=path, dir_out=dout, bg_data_amp=1)
    with qpimage.QPSeries(h5file=path_out, h5mode="r") as qps:
        # background correction with same input image will result
        # in a flat QPImage.
        assert not np.all(qps[0].pha == 0)
        assert np.all(qps[0].amp == 1)

    path_out = drymass.convert(path_in=path, dir_out=dout, bg_data_pha=1)
    with qpimage.QPSeries(h5file=path_out, h5mode="r") as qps:
        # background correction with same input image will result
        # in a flat QPImage.
        assert np.all(qps[0].pha == 0)
        assert not np.all(qps[0].amp == 1)

    try:
        os.remove(path)
    except OSError:
        pass
    shutil.rmtree(dout, ignore_errors=True)


def test_bg_correction_path():
    _qpi, path, dout = setup_test_data(num=2)
    _bgqpi, bgpath, bgdout = setup_test_data(num=1)

    path_out = drymass.convert(path_in=path, dir_out=dout,
                               bg_data_pha=bgpath,
                               bg_data_amp=bgpath)
    with qpimage.QPSeries(h5file=path_out, h5mode="r") as qps:
        # background correction with same input image will result
        # in a flat QPImage.
        assert np.all(qps[0].pha == 0)
        assert np.all(qps[0].amp == 1)

    try:
        os.remove(path)
        os.remove(bgpath)
    except OSError:
        pass
    shutil.rmtree(dout, ignore_errors=True)
    shutil.rmtree(bgdout, ignore_errors=True)


def test_change_wavelength():
    _qpi, path, dout = setup_test_data()
    path_out = drymass.convert(path_in=path,
                               dir_out=dout,
                               meta_data={"wavelength": 500e-9})

    with qpimage.QPSeries(h5file=path_out, h5mode="r") as qpso:
        id1 = qpso.identifier

    path_out2 = drymass.convert(path_in=path,
                                dir_out=dout,
                                meta_data={"wavelength": 333e-9})

    with qpimage.QPSeries(h5file=path_out2, h5mode="r") as qpso:
        id2 = qpso.identifier

    assert id1 != id2, "Files should have different identifiers"

    try:
        os.remove(path)
    except OSError:
        pass
    shutil.rmtree(dout, ignore_errors=True)


def test_reuse():
    _qpi, path, dout = setup_test_data(num=2)

    _po, changed1 = drymass.convert(path_in=path,
                                    dir_out=dout,
                                    bg_data_amp=1,
                                    bg_data_pha=1,
                                    ret_changed=True)
    _po, changed2 = drymass.convert(path_in=path,
                                    dir_out=dout,
                                    bg_data_amp=1,
                                    bg_data_pha=1,
                                    ret_changed=True)
    assert changed1
    assert not changed2

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
