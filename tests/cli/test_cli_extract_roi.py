import pathlib
import shutil
import tempfile

import numpy as np
import pytest
import qpimage

from drymass.cli import cli_extract_roi, config, dialog
from drymass.extractroi import FILE_ROI_DATA_TIF, FILE_SLICES


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
    path_in = tempfile.mktemp(suffix=".h5", prefix="drymass_test_cli_convert")
    path_in = pathlib.Path(path_in)
    with qpimage.QPSeries(h5file=path_in, h5mode="w", identifier="tt") as qps:
        for ii in range(num):
            qps.add_qpimage(qpi, identifier="image_{}".format(ii))
    # add drymass configuration file
    path_out = path_in.with_name(path_in.name + dialog.OUTPUT_SUFFIX)
    path_out.mkdir()
    cfg = config.ConfigFile(path_out)
    cfg.set_value(section="meta", key="pixel size um", value=pxsize*1e6)
    cfg.set_value(section="meta", key="wavelength nm", value=wavelength*1e9)
    cfg.set_value(section="meta", key="medium index", value=medium_index)
    cfg.set_value(section="specimen", key="size um",
                  value=radius_px*2*pxsize*1e6)
    return qpi, path_in, path_out


def test_base():
    _, path_in, path_out = setup_test_data(num=2)
    h5data = cli_extract_roi(path=path_in, ret_data=True)

    with qpimage.QPSeries(h5file=h5data, h5mode="r") as qps:
        assert len(qps) == 2
        # This might fail when the algorithms or default parameters for
        # finding ROIs change:
        assert qps[0].shape == (139, 139)

    # check existence of files
    pathtif = path_out / FILE_ROI_DATA_TIF
    assert pathtif.exists()
    assert pathtif.stat().st_size > 1500

    pathsl = path_out / FILE_SLICES
    assert pathsl.exists()
    assert len(pathsl.read_bytes()) > 100

    try:
        path_in.unlink()
    except OSError:
        pass
    shutil.rmtree(path_out, ignore_errors=True)


def test_exclude_roi():
    _, path_in, path_out = setup_test_data(num=2)
    cli_extract_roi(path=path_in)
    cfg = config.ConfigFile(path_out)
    h5data = cli_extract_roi(path=path_in, ret_data=True)
    with qpimage.QPSeries(h5file=h5data) as qps:
        assert len(qps) == 2

    # remove first image
    cfg.set_value(section="roi", key="ignore data", value="1.1")
    h5data = cli_extract_roi(path=path_in, ret_data=True)
    with qpimage.QPSeries(h5file=h5data) as qps:
        assert len(qps) == 1

    # remove second image
    cfg.set_value(section="roi", key="ignore data", value="2")
    h5data = cli_extract_roi(path=path_in, ret_data=True)
    with qpimage.QPSeries(h5file=h5data) as qps:
        assert len(qps) == 1

    # remove all
    cfg.set_value(section="roi", key="ignore data", value=["1", "2"])
    h5data = cli_extract_roi(path=path_in, ret_data=True)
    with qpimage.QPSeries(h5file=h5data) as qps:
        assert len(qps) == 0

    try:
        path_in.unlink()
    except OSError:
        pass
    shutil.rmtree(path_out, ignore_errors=True)


def test_exclude_roi_bad():
    _, path_in, path_out = setup_test_data(num=2)
    cli_extract_roi(path=path_in)
    cfg = config.ConfigFile(path_out)
    h5data = cli_extract_roi(path=path_in, ret_data=True)
    with qpimage.QPSeries(h5file=h5data) as qps:
        assert len(qps) == 2

    # bad image
    cfg.set_value(section="roi", key="ignore data", value="3")
    try:
        cli_extract_roi(path=path_in, ret_data=True)
    except ValueError:
        pass
    else:
        assert False

    # bad roi
    cfg.set_value(section="roi", key="ignore data", value="1.2")
    try:
        cli_extract_roi(path=path_in, ret_data=True)
    except ValueError:
        pass
    else:
        assert False

    # bad image and roi
    cfg.set_value(section="roi", key="ignore data", value="4.2")
    try:
        cli_extract_roi(path=path_in, ret_data=True)
    except ValueError:
        pass
    else:
        assert False

    try:
        path_in.unlink()
    except OSError:
        pass
    shutil.rmtree(path_out, ignore_errors=True)


def test_reuse():
    _, path_in, path_out = setup_test_data(num=2)
    cfg = config.ConfigFile(path_out)
    cfg.set_value(section="meta", key="pixel size um", value=1)

    h5data = cli_extract_roi(path=path_in, ret_data=True)

    time = h5data.stat().st_mtime

    # Do the same thing
    cli_extract_roi(path=path_in, ret_data=True)
    assert time == h5data.stat().st_mtime

    # Change something
    cfg.set_value(section="meta", key="pixel size um", value=1.01)
    cli_extract_roi(path=path_in, ret_data=True)
    assert time != h5data.stat().st_mtime

    try:
        path_in.unlink()
    except OSError:
        pass
    shutil.rmtree(path_out, ignore_errors=True)


@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_no_roi_found():
    _, path_in, _ = setup_test_data(radius_px=0)

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        # catches sys.exit() calls
        cli_extract_roi(path=path_in, ret_data=True)
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
