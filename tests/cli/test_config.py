import tempfile
import shutil

import numpy as np

from drymass.cli import config


def test_basic():
    path = tempfile.mkdtemp(prefix="drymass_test_config_")
    cfg = config.ConfigFile(path=path)
    assert isinstance(cfg["bg"], dict)
    shutil.rmtree(path, ignore_errors=True)


def test_dtype():
    path = tempfile.mkdtemp(prefix="drymass_test_config_")
    cfg = config.ConfigFile(path=path)

    cfg["specimen"] = {"size um": 11.3}
    assert np.allclose(cfg["specimen"]["size um"], 11.3)

    cfg.set_value(section="bg",
                  key="amplitude border px",
                  value=6.3)
    assert isinstance(cfg["bg"]["amplitude border px"], int)
    assert np.allclose(cfg["bg"]["amplitude border px"], 6)
    shutil.rmtree(path, ignore_errors=True)


def test_compat_013():
    path = tempfile.mkdtemp(prefix="drymass_test_config_")
    cfg = config.ConfigFile(path=path)
    # initialize config
    cfg.set_value("bg", "phase profile", "tilt")
    cfg.set_value("bg", "amplitude profile", "tilt")
    filepath = cfg.path
    # simulate old behavior
    data = filepath.open().read()
    data = data.replace(" profile = tilt\n", " profile = ramp\n")
    filepath.write_text(data)
    # check fix
    cfg2 = config.ConfigFile(path=path)
    assert cfg2["bg"]["phase profile"] == "tilt"
    assert cfg2["bg"]["amplitude profile"] == "tilt"


def test_compar_015():
    path = tempfile.mkdtemp(prefix="drymass_test_config_")
    cfg = config.ConfigFile(path=path)
    # initialize config
    cfg.set_value("roi", "dist border px", 3)
    cfg.set_value("roi", "exclude overlap px", 5)
    cfg.set_value("roi", "pad border px", 7)
    filepath = cfg.path
    # simulate old behavior
    data = filepath.open().read()
    data = data.replace("dist border px = ", "dist border = ")
    data = data.replace("exclude overlap px = ", "exclude overlap = ")
    data = data.replace("pad border px = ", "pad border = ")
    filepath.write_text(data)
    # check fix
    cfg2 = config.ConfigFile(path=path)
    assert cfg2["roi"]["dist border px"] == 3
    assert cfg2["roi"]["exclude overlap px"] == 5
    assert cfg2["roi"]["pad border px"] == 7


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
