"""Dry mass computation with radial inclusion factor

This examples illustrates the usage of the "radial inclusion factor"
which is defined in the configuration section "sphere" and used in
:py:func:`drymass.anasphere.relative_dry_mass` with the
keyword argument `rad_fact`.

The phase image is computed from two spheres whose dry masses
add up to 100pg with the larger sphere having a dry mass of 83pg.
The larger sphere is located at the center of the image which is also
used as the origin for dry mass computation. The radius of the larger
sphere is known (10µm). Thus, the corresponding radius (inner circle)
corresponds to a radial inclusion factor of 1. In DryMass, the
default radial inclusion factor is set to 1.2 (red). In some cases,
this inclusion factor must be increased or decreased depending on
whether additional information (the smaller sphere) should be included
in the dry mass computation or not.
"""
from drymass.anasphere import relative_dry_mass
import matplotlib
import matplotlib.pylab as plt
import numpy as np
import qpimage
import qpsphere

# refraction increment
alpha = .18  # [mL/g]

# general simulation parameters
medium_index = 1.333
model = "projection"
wavelength = 500e-9  # [m]
pixel_size = 1e-7  # [m]
grid_size = (400, 400)  # [px]

# sphere parameters
dry_masses = [83, 17]  # [pg]
radii = [10, 4]  # [µm]
centers = [(200, 200), (200, 340)]  # [px]

phase_data = np.zeros(grid_size, dtype=float)
for m, r, c in zip(dry_masses, radii, centers):
    # compute refractive index from dry mass
    r_m = r * 1e-6
    alpha_m3g = alpha * 1e-6
    m_g = m * 1e-12
    n = 1.333 + 3 * alpha_m3g * m_g / (4 * np.pi * (r_m**3))
    # generate example dataset
    qpi = qpsphere.simulate(radius=r_m,
                            sphere_index=n,
                            medium_index=medium_index,
                            wavelength=wavelength,
                            pixel_size=pixel_size,
                            model=model,
                            grid_size=grid_size,
                            center=c)
    phase_data += qpi.pha

qpi_sum = qpimage.QPImage(data=phase_data,
                          which_data="phase",
                          meta_data={"wavelength": wavelength,
                                     "pixel size": pixel_size,
                                     "medium index": medium_index})

# compute dry mass in dependence of radius
mass_evolution = []
mass_radii = []
for rad_fact in np.linspace(0, 2.0, 100):
    dm = relative_dry_mass(qpi=qpi_sum,
                           radius=radii[0] * 1e-6,
                           center=centers[0],
                           alpha=alpha,
                           rad_fact=rad_fact)
    mass_evolution.append(dm * 1e12)
    mass_radii.append(rad_fact)

# plot results
fig = plt.figure(figsize=(8, 3.8))
matplotlib.rcParams["image.interpolation"] = "bicubic"
# phase image
ax1 = plt.subplot(121, title="phase image [rad]")
ax1.axis("off")
map1 = ax1.imshow(qpi_sum.pha)
plt.colorbar(map1, ax=ax1, fraction=.048, pad=0.05)
# dry mass vs. inclusion factor
ax2 = plt.subplot(122, title="dry mass")
ax2.plot(mass_radii, mass_evolution)
ax2.set_ylabel("computed dry mass [pg]")
ax2.set_xlabel("radial inclusion factor")
ax2.grid()
# radius indicators
for r in [100, 180]:
    cx = centers[0][0] + .5
    cy = centers[0][1] + .5
    circle = plt.Circle((cx, cy), r,
                        color='w', fill=False, ls="dashed", lw=1, alpha=.5)
    ax1.add_artist(circle)
    ax2.axvline(r / 100, color="#404040", ls="dashed")
# add default
circle = plt.Circle((cx, cy), 120,
                    color='r', fill=False, ls="dashed", lw=1, alpha=.5)
ax1.add_artist(circle)
ax2.axvline(1.2, color="r", ls="dashed")

plt.tight_layout()
plt.show()
