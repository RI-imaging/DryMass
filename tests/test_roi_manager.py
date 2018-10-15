import pathlib
import tempfile
import shutil
import warnings

from drymass import roi


def test_basic():
    rmg = roi.ROIManager(identifier="test")
    assert len(rmg) == 0

    roi_slice = slice(4, 10), slice(5, 10)
    image_index = 2
    roi_index = 5
    identifier = "test_2_5"
    rmg.add(roi_slice, image_index, roi_index, identifier)
    assert len(rmg) == 1

    regions = rmg.get_from_image_index(image_index)
    reg = regions[0]
    assert reg.identifier == identifier
    assert reg.roi_slice == roi_slice


def test_save_load():
    rmg = roi.ROIManager(identifier="test")
    assert len(rmg) == 0

    roi_index = 5
    identifier = "test_2_5"
    for ii in [2, 5, 7]:
        image_index = ii
        identifier = "test_{}".format(image_index)
        roislice = slice(4+ii, 10+ii), slice(5, 10)
        rmg.add(roislice, image_index, roi_index, identifier)

    tdir = tempfile.mkdtemp(prefix="test_drymass_roi_manager_")
    path = pathlib.Path(tdir) / "test_roi.txt"
    rmg.save(path)

    rmg2 = roi.ROIManager(identifier="test_")
    rmg2.load(path)

    assert len(rmg) == len(rmg2)

    for ii in [2, 5, 7]:
        assert rmg2.get_from_image_index(ii) == rmg.get_from_image_index(ii)

    shutil.rmtree(tdir, ignore_errors=True)


def test_valueerror():
    try:
        roi.ROIManager(identifier=2)
    except ValueError:
        pass
    else:
        assert False, "identifier must be string or None"

    rmg = roi.ROIManager()
    roislice = slice(4, 10), slice(5, 10)
    image_index = 2
    roi_index = 5
    identifier = "test_2_5"

    try:  # bad roislice
        rmg.add(roislice[0], image_index, roi_index, identifier)
    except ValueError:
        pass
    else:
        assert False, "bad roi slice"

    try:  # bad identifier
        rmg.add(roislice, image_index, roi_index, None)
    except ValueError:
        pass
    else:
        assert False, "bad identifier"


def test_identifier_warnging():
    rmg = roi.ROIManager(identifier="not_in_roi_slice")
    roislice = slice(4, 10), slice(5, 10)
    image_index = 2
    roi_index = 5
    with warnings.catch_warnings(record=True) as w:
        # Cause all warnings to always be triggered.
        warnings.simplefilter("always")
        # Trigger a warning.
        rmg.add(roislice, image_index, roi_index, "testA")
        # Verify some things
        assert len(w) == 1
        assert issubclass(w[-1].category, roi.ROIManagerWarning)
        assert "does not match that of QPSeries" in str(w[-1].message)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
