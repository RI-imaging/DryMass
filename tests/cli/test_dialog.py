import pathlib
import shutil
import tempfile

import numpy as np
import qpimage

from drymass.cli import config, dialog


def setup_test_data(radius_px=30, size=200, pxsize=1e-6, medium_index=1.335,
                    wavelength=550e-9, method="edge", model="projection",
                    refraction_increment=.18, num=1, write_config=True):
    x = np.arange(size).reshape(-1, 1)
    y = np.arange(size).reshape(1, -1)
    cx = 80
    cy = 120
    r = np.sqrt((x - cx)**2 + (y - cy)**2)
    pha = (r < radius_px) * 1.3
    amp = .5 + np.roll(pha, 10) / pha.max()
    qpi = qpimage.QPImage(data=(pha, amp), which_data="phase,amplitude")
    path_in = tempfile.mktemp(suffix=".h5", prefix="drymass_test_cli_dialog")
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
        cfg.set_value(section="sphere", key="method", value=method)
        cfg.set_value(section="sphere", key="model", value=model)
        cfg.set_value(section="sphere", key="refraction increment",
                      value=refraction_increment)
    return qpi, path_in, path_out


def test_merge_config():
    # test data
    _, path_in, path_out = setup_test_data(medium_index=1.30,
                                           pxsize=1.12e-6,
                                           method="image",
                                           model="projection",
                                           refraction_increment=1.1)

    # profile
    _, path_profile = tempfile.mkstemp(
        prefix="drymass_test_config_", suffix=".cfg")
    cfg = config.ConfigFile(path=path_profile)
    cfg.path.write_text("[meta]\n"
                        + "medium index = 1.31\n"
                        + "pixel size um = None\n"
                        + "[sphere]\n"
                        + "method = image\n"
                        + "model = rytov\n")

    cfg2 = config.ConfigFile(path=path_out)
    assert cfg2["sphere"]["refraction increment"] == 1.1, "for test case"
    assert cfg2["meta"]["pixel size um"] == 1.12, "for test case"

    # apply profile (merge with original configuration)
    dialog.main(path=path_in, profile=path_profile)

    # Sanity checks in case DryMass defaults changed
    assert cfg["sphere"]["refraction increment"] != 1.1, "for test case"
    assert cfg["meta"]["pixel size um"] != 1.12, "for test case"

    # The following three are all valid by just copying cfg to path_out
    assert cfg2["meta"]["medium index"] == 1.31
    assert cfg2["sphere"]["method"] == "image"
    assert cfg2["sphere"]["model"] == "rytov"
    # This one is only valid when the configs are merged
    assert cfg2["sphere"]["refraction increment"] == 1.1
    # This one is only valid when Nones in profile do not override path_out
    assert cfg2["meta"]["pixel size um"] == 1.12

    try:
        cfg.path.unlink()
        cfg2.path.unlink()
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
