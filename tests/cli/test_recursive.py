import pathlib
import shutil
import tempfile

import numpy as np
import qpimage

from drymass.cli import config, dialog
import qpformat


def setup_test_data(radius_px=30, size=200, pxsize=1e-6, medium_index=1.335,
                    wavelength=550e-9, num=1, write_config=True, path_in=None):
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
    if path_in is None:
        path_in = tempfile.mktemp(suffix=".h5",
                                  prefix="drymass_test_cli_convert")
    path_in = pathlib.Path(path_in)
    with qpimage.QPSeries(h5file=path_in, h5mode="w", identifier="tes") as qps:
        for ii in range(num):
            qps.add_qpimage(qpi, identifier="test_{}".format(ii))
    path_out = path_in.with_name(path_in.name + dialog.OUTPUT_SUFFIX)
    path_out.mkdir()
    if write_config:
        # add drymass configuration file
        cfg = config.ConfigFile(path_out)
        cfg.set_value(section="meta", key="pixel size um", value=pxsize*1e6)
        cfg.set_value(section="meta", key="wavelength nm",
                      value=wavelength*1e9)
        cfg.set_value(section="meta", key="medium index", value=medium_index)
    return qpi, path_in, path_out


def setup_test_data_recursive(n=2, **kwargs):
    path = tempfile.mkdtemp(prefix="drymass_test_cli_recurse_")
    path = pathlib.Path(path)
    for ii in range(n):
        path_in = path / "sub_{}.h5".format(ii)
        setup_test_data(path_in=path_in, **kwargs)
    return path


def test_simple_qpseries():
    path = setup_test_data_recursive(n=2, num=3)

    ps = dialog.recursive_search(path)
    assert len(ps) == 2

    # make sure files are the right ones
    for ii in range(len(ps)):
        with qpimage.QPSeries(h5file=ps[ii], h5mode="r") as qps:
            assert len(qps) == 3

    shutil.rmtree(path, ignore_errors=True)


def test_qpseries_with_bad_data():
    path = setup_test_data_recursive(n=2, num=3)

    (path / "bad_data.h5").write_text("This file should be ignored.")

    ps = dialog.recursive_search(path)
    assert len(ps) == 2

    # make sure files are the right ones
    for ii in range(len(ps)):
        with qpimage.QPSeries(h5file=ps[ii], h5mode="r") as qps:
            assert len(qps) == 3

    shutil.rmtree(path, ignore_errors=True)


def test_complex_qpseries():
    path = tempfile.mkdtemp(prefix="drymass_test_cli_recurse2_")
    path = pathlib.Path(path)
    paths = [path / "1" / "2",
             path / "3",
             path / "4" / "5" / "6"
             ]
    for pp in paths:
        pp.mkdir(parents=True, exist_ok=True)
        setup_test_data(path_in=pp / "test.h5")

    ps = dialog.recursive_search(path)
    for ii, pi in enumerate(ps):
        assert pi == paths[ii] / "test.h5"

    shutil.rmtree(path, ignore_errors=True)


def test_complex_folder_with_unused_qpseries():
    path = tempfile.mkdtemp(prefix="drymass_test_cli_recurse2_")
    path = pathlib.Path(path)
    qpi, _, _ = setup_test_data(num=1, path_in=path / "test.h5")

    path = pathlib.Path(path)
    paths = [path / "1" / "2",
             path / "3",
             path / "4" / "5" / "6"
             ]
    for pp in paths:
        pp.mkdir(parents=True, exist_ok=True)
        for ii in range(4):
            qpi.copy(h5file=pp / "test_{}.h5".format(ii))

    ps = dialog.recursive_search(path)
    for ii, pi in enumerate(ps):
        assert pi == paths[ii]
    shutil.rmtree(path, ignore_errors=True)


def test_recursive_root_include1():
    qpi, path_in, path_out = setup_test_data(num=2)
    ps = dialog.recursive_search(path_in)
    assert len(ps) == 1
    assert ps[0] == path_in
    try:
        path_in.unlink()
    except OSError:
        pass
    shutil.rmtree(path_out, ignore_errors=True)


def test_recursive_root_include2():
    path = tempfile.mkdtemp(prefix="drymass_test_cli_recurse2_")
    path = pathlib.Path(path)
    # this file will be ignored
    qpi, ignored_path, _ = setup_test_data(num=1, path_in=path / "test.h5")

    for ii in range(4):
        qpi.copy(h5file=path / "test_{}.h5".format(ii))

    ps = dialog.recursive_search(path)
    assert len(ps) == 1
    assert ignored_path not in ps

    ds = qpformat.load_data(path=path)
    assert len(ds) == 4

    shutil.rmtree(path, ignore_errors=True)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
