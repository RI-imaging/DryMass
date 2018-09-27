import pathlib
import shutil
import tempfile

import numpy as np
import qpimage

from drymass.cli import cli_convert, config, dialog


def setup_test_data(radius_px=30, size=200, pxsize=1e-6, medium_index=1.335,
                    wavelength=550e-9, num=1, write_config=True):
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


def test_base():
    qpi, path_in, path_out = setup_test_data(num=2)
    h5data = cli_convert(path=path_in, ret_data=True)

    with qpimage.QPSeries(h5file=h5data, h5mode="r") as qps:
        assert np.allclose(qpi.pha, qps[0].pha)
        assert np.allclose(qpi.amp, qps[0].amp)

    try:
        path_in.unlink()
    except OSError:
        pass
    shutil.rmtree(path_out, ignore_errors=True)


def test_bg_corr_file():
    _bgqpi, bg_path_in, bg_path_out = setup_test_data(num=1)
    _qpi, path_in, path_out = setup_test_data(num=2)
    cfg = config.ConfigFile(path_out)
    cfg.set_value(section="bg", key="phase data", value=bg_path_in)
    cfg.set_value(section="bg", key="amplitude data", value=bg_path_in)
    h5data = cli_convert(path=path_in, ret_data=True)

    with qpimage.QPSeries(h5file=h5data, h5mode="r") as qps:
        assert np.all(qps[0].pha == 0)
        assert np.all(qps[0].amp == 1)

    try:
        path_in.unlink()
        bg_path_in.unlink()
    except OSError:
        pass
    shutil.rmtree(path_out, ignore_errors=True)
    shutil.rmtree(bg_path_out, ignore_errors=True)


def test_bg_corr_file_relative():
    _bgqpi, bg_path_in, bg_path_out = setup_test_data(num=1)
    _qpi, path_in, path_out = setup_test_data(num=2)
    cfg = config.ConfigFile(path_out)
    cfg.set_value(section="bg", key="phase data",
                  value=str(bg_path_in.relative_to(path_in.parent)))
    cfg.set_value(section="bg", key="amplitude data",
                  value=str(bg_path_in.relative_to(path_in.parent)))
    h5data = cli_convert(path=path_in, ret_data=True)

    with qpimage.QPSeries(h5file=h5data, h5mode="r") as qps:
        assert np.all(qps[0].pha == 0)
        assert np.all(qps[0].amp == 1)

    try:
        path_in.unlink()
        bg_path_in.unlink()
    except OSError:
        pass
    shutil.rmtree(path_out, ignore_errors=True)
    shutil.rmtree(bg_path_out, ignore_errors=True)


def test_bg_corr_index():
    _qpi, path_in, path_out = setup_test_data(num=2)
    cfg = config.ConfigFile(path_out)
    cfg.set_value(section="bg", key="phase data", value=1)
    cfg.set_value(section="bg", key="amplitude data", value=1)
    h5data = cli_convert(path=path_in, ret_data=True)

    with qpimage.QPSeries(h5file=h5data, h5mode="r") as qps:
        assert np.all(qps[0].pha == 0)
        assert np.all(qps[0].amp == 1)

    try:
        path_in.unlink()
    except OSError:
        pass
    shutil.rmtree(path_out, ignore_errors=True)


def test_extract_meta_data():
    """qpformat can automatically transfer the metadata from
    QPSeries files to the dataset which DryMass makes use of.
    """
    _qpi, path_in, path_out = setup_test_data(pxsize=1.3e-6,
                                              medium_index=1.345,
                                              wavelength=555e-9,
                                              num=2,
                                              write_config=False)

    cli_convert(path=path_in)
    cfg = config.ConfigFile(path_out)

    assert cfg["meta"]["medium index"] == 1.345
    assert cfg["meta"]["pixel size um"] == 1.3
    assert cfg["meta"]["wavelength nm"] == 555

    try:
        path_in.unlink()
    except OSError:
        pass
    shutil.rmtree(path_out, ignore_errors=True)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
