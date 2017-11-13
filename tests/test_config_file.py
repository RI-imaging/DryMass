import tempfile
import shutil

import numpy as np

from drymass import config_file


def test_basic():
    path = tempfile.mkdtemp(prefix="drymass_test_config_")
    cfg = config_file.ConfigFile(path=path)
    assert isinstance(cfg["bg"], dict)
    shutil.rmtree(path, ignore_errors=True)


def test_dtype():
    path = tempfile.mkdtemp(prefix="drymass_test_config_")
    cfg = config_file.ConfigFile(path=path)

    cfg["specimen"] = {"size um": 11.3}
    assert np.allclose(cfg["specimen"]["size um"], 11.3)

    cfg.set_value(section="bg",
                  key="amplitude border px",
                  value=6.3)
    assert isinstance(cfg["bg"]["amplitude border px"], int)
    assert np.allclose(cfg["bg"]["amplitude border px"], 6)
    shutil.rmtree(path, ignore_errors=True)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
