import pathlib

import numpy as np
import qpimage
import qpsphere


FILE_SPHERE_DATA = "sphere_{}_{}_data.h5"
FILE_SPHERE_STAT = "sphere_{}_{}_statistics.txt"


def analyze_sphere(h5roiseries, dir_out, r0=10e-6, method="edge",
                   model="projection", edgekw={}, alpha=2e-4, rad_fact=1.2):

    dir_out = pathlib.Path(dir_out).resolve()

    h5out = dir_out / FILE_SPHERE_DATA.format(method, model)
    statout = dir_out / FILE_SPHERE_STAT.format(method, model)

    with qpimage.QPSeries(h5file=h5roiseries, h5mode="r") as qps_in, \
            qpimage.QPSeries(h5file=h5out, h5mode="w") as qps_out, \
            statout.open(mode="w") as fd:

        header = ["object",
                  "index",
                  "radius_um",
                  "rel_dry_mass_pg",
                  "abs_dry_mass_pg",
                  "time",
                  "medium",
                  ]
        fd.write("#" + "\t".join(header) + "\r\n")

        for qpi in qps_in:
            # determine parameters
            n, r, c = qpsphere.analyze(qpi,
                                       r0=r0,
                                       method=method,
                                       model=model,
                                       ret_center=True,
                                       edgekw=edgekw)
            # save in txt file
            data = {"object": qpi["identifier"],
                    "index": n,
                    "radius_um": r * 1e6,
                    "abs_dry_mass_pg": absolute_dry_mass_sphere(
                qpi=qpi,
                radius=r,
                center=c,
                alpha=alpha,
                rad_fact=rad_fact
            ) * 1e12,
                "rel_dry_mass_pg": relative_dry_mass(
                qpi=qpi,
                radius=r,
                center=c,
                alpha=alpha,
                rad_fact=rad_fact
            ) * 1e12,
                "time": qpi["time"],
                "medium": qpi["medium index"]
            }
            fd.write("\t".join([str(data[k]) for k in header]) + "\r\n")
            # save simulation data
            qpi_model = qpsphere.simulate(radius=r,
                                          sphere_index=n,
                                          medium_index=qpi["medium index"],
                                          wavelength=qpi["wavelength"],
                                          pixel_size=qpi["pixel size"],
                                          model=model,
                                          grid_size=qpi.shape,
                                          center=c)
            qps_out.add_qpimage(qpi=qpi_model, identifier=qpi["identifier"])

    return h5out


def absolute_dry_mass_sphere(qpi, radius, center, alpha=.18, rad_fact=1.2):
    """Compute absolute dry mass of a spherical phase object

    The absolute dry mass is computed with

    m_abs = m_rel + m_sup
    m_rel = lambda / (2*PI*alpha) * phi_tot * deltaA
    m_sup = 4*PI / (3*alpha) * radius^3 (n_med - n_water)

    with the vacuum wavelength `lambda`, the total phase
    retardation in the area of interest `phi_tot`, the pixel
    area `deltaA`, the refractive index of the medium `n_med`
    (stored in `qpi.meta`), and the refractive index of water
    `n_water`=1.333.

    This is the *absolute* dry mass, because it takes into account
    the offset caused by the suppressed density in the phase data.

    Parameters
    ----------
    qpi: qpimage.QPImage
        QPI data
    center: tuble (x,y)
        Center of the sphere [px]
    radius: float
        Radius of the sphere [m]
    wavelength: float
        The wavelength of the light [m]
    alpha: float
        Refraction increment [mL/g]
    rad_fact: float
        Inclusion factor that scales `radius` to increase
        the area used for phase summation; if the backgound
        phase exhibits a noise phase signal, positive and
        negative contributions cancel out and `rad_fact`
        does not have an effect above a certain critical value.

    Returns
    -------
    dry_mass: float
        The absolute dry mass of the sphere [g]
    """
    dm_rel = relative_dry_mass(qpi=qpi,
                               radius=radius,
                               center=center,
                               alpha=alpha,
                               rad_fact=rad_fact)
    medium_index = qpi["medium index"]
    dm_sup = 4 / 3 * np.pi / (alpha * 1e-6) * \
        radius**3 * (medium_index - 1.333)
    return dm_rel + dm_sup


def relative_dry_mass(qpi, radius, center, alpha=.18, rad_fact=1.2):
    """Compute relative dry mass of a circular area in QPI

    The dry mass is computed with

    m_rel = lambda / (2*PI*alpha) * phi_tot * deltaA

    with the vacuum wavelength `lambda`, the total phase
    retardation in the area of interest `phi_tot`, and the pixel
    area `deltaA`.

    This is the *relative* dry mass, because it is computed relative
    to the surrounding medium (phi_tot) and not relative to water.

    Parameters
    ----------
    qpi: qpimage.QPImage
        QPI data
    center: tuble (x,y)
        Center of the area of interest [px]
    radius: float
        Radius of the area of interest [m]
    wavelength: float
        The wavelength of the light [m]
    alpha: float
        Refraction increment [mL/g]
    rad_fact: float
        Inclusion factor that scales `radius` to increase
        the area used for phase summation; if the backgound
        phase exhibits a noise phase signal, positive and
        negative contributions cancel out and `rad_fact`
        does not have an effect above a certain critical value.

    Returns
    -------
    dry_mass: float
        The relative dry mass of the object [g]
    """
    image = qpi.pha
    rincl = radius / qpi["pixel size"] * rad_fact
    wavelength = qpi["wavelength"]
    sx, sy = qpi.shape
    x = np.arange(sx).reshape(-1, 1)
    y = np.arange(sy).reshape(1, -1)
    discsq = ((x - center[0])**2 + (y - center[1])**2)
    area = discsq < rincl**2
    phi_tot = np.sum(image[area])
    # compute dry mass
    pxarea = qpi["pixel size"]**2
    # convert alpha mL/g to m³/g
    fact = 1e-6
    # [kg]
    dm = wavelength / (2 * np.pi * alpha * fact) * phi_tot * pxarea
    return dm
