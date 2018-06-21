import numpy as np
import qpimage

from drymass import search


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
    rois = search.search_objects_base(image=image, size=2 * radius)
    roi = rois[0]
    assert np.allclose(roi.equivalent_diameter, 2 * radius, atol=.2, rtol=0)
    assert np.allclose(roi.centroid, (cx, cy))


def test_bg_overlap():
    size = 200
    x = np.arange(size).reshape(-1, 1)
    y = np.arange(size).reshape(1, -1)
    # 5 px between regions
    cx1 = 100
    cy1 = 100
    cx2 = 100
    cy2 = 145
    radius = 20
    r1 = np.sqrt((x - cx1)**2 + (y - cy1)**2)
    r2 = np.sqrt((x - cx2)**2 + (y - cy2)**2)
    raw_pha = (r1 < radius) * 1.3
    bg_pha = (r2 < radius) * 1.2
    # create data set
    qpi = qpimage.QPImage(data=raw_pha, bg_data=bg_pha,
                          which_data="phase",
                          meta_data={"pixel size": 1e-6})
    slices1 = search.search_phase_objects(qpi=qpi,
                                          size_m=2 * radius *
                                          qpi["pixel size"],
                                          exclude_overlap=0)
    slices2 = search.search_phase_objects(qpi=qpi,
                                          size_m=2 * radius * 1e-6,
                                          exclude_overlap=10)
    assert len(slices1) == 1
    assert len(slices2) == 0


def test_padding():
    size = 200
    x = np.arange(size).reshape(-1, 1)
    y = np.arange(size).reshape(1, -1)
    cx = 80
    cy = 120
    radius = 30
    r = np.sqrt((x - cx)**2 + (y - cy)**2)
    image = (r < radius) * 1.3
    pxsize = 1e-6
    qpi = qpimage.QPImage(data=image,
                          which_data="phase",
                          meta_data={"pixel size": pxsize})
    paddiff = 7
    [slice1] = search.search_phase_objects(qpi=qpi,
                                           size_m=2 * radius * pxsize,
                                           pad_border=0,
                                           )
    [slice2] = search.search_phase_objects(qpi=qpi,
                                           size_m=2 * radius * pxsize,
                                           pad_border=paddiff,
                                           )
    [slice3] = search.search_phase_objects(qpi=qpi,
                                           size_m=2 * radius * pxsize,
                                           pad_border=100,
                                           )
    dx1 = slice1[0].stop - slice1[0].start
    dy1 = slice1[1].stop - slice1[1].start
    dx2 = slice2[0].stop - slice2[0].start
    dy2 = slice2[1].stop - slice2[1].start
    dx3 = slice3[0].stop - slice3[0].start
    dy3 = slice3[1].stop - slice3[1].start
    assert dx2 - dx1 == 2 * paddiff
    assert dy2 - dy1 == 2 * paddiff
    assert dx3 == size
    assert dy3 == size
    assert slice3[0].start == 0
    assert slice3[1].start == 0


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
