import argparse
import pathlib
import shutil
import tempfile
import warnings

import numpy as np
import qpimage

from drymass.cli import cli_convert, config, dialog, profile


def setup_config(pxsize=1e-6, medium_index=1.335, wavelength=550e-9):
    _, path = tempfile.mkstemp(prefix="drymass_test_config_", suffix=".cfg")
    cfg = config.ConfigFile(path=path)
    cfg.set_value("bg", "phase profile", "tilt")
    cfg.set_value("bg", "amplitude profile", "tilt")
    cfg.set_value("roi", "dist border px", 3)
    cfg.set_value("roi", "exclude overlap px", 5)
    cfg.set_value("roi", "pad border px", 7)
    cfg.set_value(section="meta", key="pixel size um", value=pxsize*1e6)
    cfg.set_value(section="meta", key="wavelength nm",
                  value=wavelength*1e9)
    cfg.set_value(section="meta", key="medium index", value=medium_index)

    return cfg.path


def setup_test_data(radius_px=30, size=200, num=1):
    x = np.arange(size).reshape(-1, 1)
    y = np.arange(size).reshape(1, -1)
    cx = 80
    cy = 120
    r = np.sqrt((x - cx)**2 + (y - cy)**2)
    pha = (r < radius_px) * 1.3
    amp = .5 + np.roll(pha, 10) / pha.max()
    qpi = qpimage.QPImage(data=(pha, amp), which_data="phase,amplitude")
    path_in = tempfile.mktemp(suffix=".h5", prefix="drymass_test_cli_profile")
    path_in = pathlib.Path(path_in)
    with qpimage.QPSeries(h5file=path_in, h5mode="w", identifier="tes") as qps:
        for ii in range(num):
            qps.add_qpimage(qpi, identifier="test_{}".format(ii))
    path_out = path_in.with_name(path_in.name + dialog.OUTPUT_SUFFIX)
    path_out.mkdir()
    return qpi, path_in, path_out


def test_add_fail():
    path = setup_config()
    argsadd = argparse.Namespace(subparser_name="add",
                                 name="test_8473_prof",
                                 path=path)
    profile.cli_profile(args=argsadd)
    try:
        profile.cli_profile(args=argsadd)
    except OSError:
        pass
    else:
        assert False
    # remove the profile again
    argsrem = argparse.Namespace(subparser_name="remove",
                                 name="test_8473_prof")
    profile.cli_profile(args=argsrem)
    try:
        path.unlink()
    except OSError:
        pass


def test_add_remove():
    path = setup_config()
    argsadd = argparse.Namespace(subparser_name="add",
                                 name="test_8472_prof",
                                 path=path)
    profile.cli_profile(args=argsadd)
    # verify that the profile was imported
    pps = profile.get_profile_path(name="test_8472_prof")
    assert pps.exists()
    # remove the profile again
    argsrem = argparse.Namespace(subparser_name="remove",
                                 name="test_8472_prof")
    profile.cli_profile(args=argsrem)
    assert not pps.exists()
    try:
        path.unlink()
    except OSError:
        pass


def test_convert_with_profile():
    cfgpath = setup_config(pxsize=1.34e-6,
                           medium_index=1.346,
                           wavelength=554.2e-9)
    _, path_in, path_out = setup_test_data()
    argsadd = argparse.Namespace(subparser_name="add",
                                 name="test_8440_prof_convert",
                                 path=cfgpath)
    profile.cli_profile(args=argsadd)
    # perform conversion
    h5data = cli_convert(path=path_in,
                         ret_data=True,
                         profile="test_8440_prof_convert")
    cfg = config.ConfigFile(path_out)
    assert np.allclose(cfg["meta"]["medium index"], 1.346)
    assert np.allclose(cfg["meta"]["pixel size um"], 1.34)
    assert np.allclose(cfg["meta"]["wavelength nm"], 554.2)

    with qpimage.QPSeries(h5file=h5data, h5mode="r") as qps:
        assert np.allclose(qps[0]["medium index"], 1.346)
        assert np.allclose(qps[0]["pixel size"], 1.34e-6)
        assert np.allclose(qps[0]["wavelength"], 554.2e-9)

    # cleanup
    argsrem = argparse.Namespace(subparser_name="remove",
                                 name="test_8440_prof_convert")
    profile.cli_profile(args=argsrem)
    try:
        cfgpath.unlink()
        path_in.unlink()
    except OSError:
        pass
    shutil.rmtree(path_out, ignore_errors=True)


def test_export():
    path = setup_config()
    argsadd = argparse.Namespace(subparser_name="add",
                                 name="test_8491_prof",
                                 path=path)
    profile.cli_profile(args=argsadd)
    # export
    tdir = tempfile.mkdtemp(prefix="test_drymass_profile_export_")
    argsexp = argparse.Namespace(subparser_name="export",
                                 path=tdir)
    profile.cli_profile(args=argsexp)
    assert (pathlib.Path(tdir) / "profile_test_8491_prof.cfg").exists()
    # cleanup
    argsrem = argparse.Namespace(subparser_name="remove",
                                 name="test_8491_prof")
    profile.cli_profile(args=argsrem)
    shutil.rmtree(tdir, ignore_errors=True)
    try:
        path.unlink()
    except OSError:
        pass


def test_get_profile_path():
    path = setup_config()
    assert path == profile.get_profile_path(name=path)
    try:
        path.unlink()
    except OSError:
        pass


def test_list_none(capsys):
    if profile.get_profiles():
        warnings.warn("Test cannot succeed, b/c there are user profiles.")
    else:
        argslist = argparse.Namespace(subparser_name="list")
        profile.cli_profile(args=argslist)
        captured = capsys.readouterr()
        assert captured.out.strip() == "No profiles in local library."


def test_list_profile(capsys):
    path = setup_config()
    argsadd = argparse.Namespace(subparser_name="add",
                                 name="test_8490_prof",
                                 path=path)
    profile.cli_profile(args=argsadd)
    argslist = argparse.Namespace(subparser_name="list")
    profile.cli_profile(args=argslist)
    captured = capsys.readouterr()
    assert "- test_8490_prof:" in captured.out.strip()
    argsrem = argparse.Namespace(subparser_name="remove",
                                 name="test_8490_prof")
    profile.cli_profile(args=argsrem)
    try:
        path.unlink()
    except OSError:
        pass


def test_remove_fail():
    argsrem = argparse.Namespace(subparser_name="remove",
                                 name="test_8474_prof")
    try:
        profile.cli_profile(args=argsrem)
    except OSError:
        pass
    else:
        assert False


if __name__ == "__main__":
    # Run all tests
    print("Cannot run all tests b/c of usage of `capsys` fixture! "
          "Please use py.test.")
