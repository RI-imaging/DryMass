import pathlib
import shutil
import tempfile

import numpy as np
import qpimage

from drymass.cli import cli_analyze_sphere, config, dialog
from drymass.anasphere import FILE_SPHERE_DATA, FILE_SPHERE_STAT


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
    path_in = tempfile.mktemp(suffix=".h5", prefix="drymass_test_cli_sphere")
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
    h5data = cli_analyze_sphere(path=path_in, ret_data=True)

    with qpimage.QPSeries(h5file=h5data, h5mode="r") as qps:
        assert len(qps) == 2

    # This might fail if the default kwargs for sphere analysis change
    assert h5data == path_out / FILE_SPHERE_DATA.format("edge", "projection")

    # check existence of files
    assert h5data.exists()
    assert h5data.stat().st_size > 10000

    pathsl = path_out / FILE_SPHERE_STAT.format("edge", "projection")
    assert pathsl.exists()
    assert len(pathsl.read_bytes()) > 100

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
