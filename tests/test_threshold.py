import numpy as np

from drymass import threshold as thr


def test_basic():
    size = 200
    image = np.zeros((size, size), dtype=float)
    x = np.arange(size).reshape(-1, 1)
    y = np.arange(size).reshape(1, -1)
    cx = 80
    cy = 120
    radius = 30
    r = np.sqrt((x - cx)**2 + (y - cy)**2)
    image[r < radius] = 1.3
    assert np.all(thr.image2mask(image, 1) == (r < radius))
    assert np.all(thr.image2mask(image, "dm-nuclei") == (r < radius))


def test_invert():
    size = 200
    image = np.zeros((size, size), dtype=float)
    x = np.arange(size).reshape(-1, 1)
    y = np.arange(size).reshape(1, -1)
    cx = 80
    cy = 120
    radius = 30
    r = np.sqrt((x - cx)**2 + (y - cy)**2)
    image[r < radius] = 1.3
    normal = thr.image2mask(image, 1)
    invert = thr.image2mask(image, 1, invert=True)
    assert np.all(normal == ~invert)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
