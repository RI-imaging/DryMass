import numpy as np
import qpsphere

from drymass.anasphere import absolute_dry_mass_sphere, relative_dry_mass


def defaultsim(medium_index=1.335,
               m_g=150e-12):
    grid_size = (100, 100)
    center = (50, 50)
    wavelength = 550 * 1e-9
    pixel_size = .3 * 1e-6
    r_m = 10 * 1e-6
    alpha = .18
    alpha_m3g = alpha * 1e-6
    n = 1.335 + 3 * alpha_m3g * m_g / (4 * np.pi * (r_m**3))
    # generate example dataset
    qpi = qpsphere.simulate(radius=r_m,
                            sphere_index=n,
                            medium_index=medium_index,
                            wavelength=wavelength,
                            pixel_size=pixel_size,
                            model="projection",
                            grid_size=grid_size,
                            center=center)
    kwargs = {"qpi": qpi,
              "radius": r_m,
              "center": center,
              "alpha": alpha,
              "rad_fact": 1.2
              }
    return kwargs


def test_equivalence():
    m_g = 150e-12
    kwargs = defaultsim(m_g=m_g)
    mabs = absolute_dry_mass_sphere(**kwargs)
    mrel = relative_dry_mass(**kwargs)
    assert mabs == mrel
    assert np.allclose(mabs, m_g, atol=0, rtol=.0005)


def test_higher_medium():
    for m_g in np.linspace(30e-12, 150e-12, 4):
        for medium_index in np.linspace(1.334, 1.34, 8):
            kwargs = defaultsim(m_g=m_g, medium_index=medium_index)
            mabs = absolute_dry_mass_sphere(**kwargs)
            # accuracy depends on image resolution
            assert np.allclose(mabs, m_g, atol=0, rtol=.002)


def test_negative():
    m_g = 5e-12
    medium_index = 1.336
    kwargs = defaultsim(m_g=m_g, medium_index=medium_index)
    mrel = relative_dry_mass(**kwargs)
    mabs = absolute_dry_mass_sphere(**kwargs)
    assert mrel < 0
    assert np.allclose(mabs, m_g, atol=0, rtol=.002)


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
