import pathlib

import numpy as np
import qpimage
import qpsphere


FILE_SPHERE_DATA = "sphere_{}_{}_data.h5"
FILE_SPHERE_STAT = "sphere_{}_{}_statistics.txt"


def analyze_sphere(h5roiseries, dir_out, n0=1.37, r0=10e-6, method="edge",
                   model="projection", alpha=2e-4, rad_fact=1.2):

    dir_out = pathlib.Path(dir_out).resolve()

    h5out = dir_out / FILE_SPHERE_DATA.format(method, model)
    statout = dir_out / FILE_SPHERE_STAT.format(method, model)

    with qpimage.QPSeries(h5file=h5roiseries, h5mode="r") as qps_in, \
            qpimage.QPSeries(h5file=h5out, h5mode="w") as qps_out, \
            statout.open(mode="w") as fd:

        header = ["object",
                  "index",
                  "radius_um",
                  "dry_mass_pg",
                  "time",
                  "medium",
                  ]
        fd.write("#" + "\t".join(header) + "\r\n")

        for qpi in qps_in:
            # determine parameters
            n, r, c = qpsphere.analyze(qpi,
                                       n0=n0,
                                       r0=r0,
                                       method=method,
                                       model=model,
                                       ret_center=True)
            # save in txt file
            data = {"object": qpi["identifier"],
                    "index": n,
                    "radius_um": r * 1e6,
                    "dry_mass_pg": compute_dry_mass(qpi=qpi,
                                                    r=r,
                                                    center=c,
                                                    alpha=alpha,
                                                    rad_fact=rad_fact),
                    "time": qpi["time"],
                    "medium": qpi["medium index"]
                    }
            fd.write("\t".join([str(data[k]) for k in header]) + "\r\n")
            # save modeled output
            qps_out


def compute_dry_mass(qpi, r, center, alpha=2e-4, rad_fact=1.2):
    """Compute dry mass of a circular area in QPI

    The dry mass is given by

    m = lambda / (2*PI*alpha) * iint phi(x,y) dx dy
      = lambda / (2*PI*alpha) * phi_tot * deltaA

    with
    - alpha: refraction increment [m³/kg]
    - lambda: wavelength [m]
    - deltaA: Area element of total area A [m²]
    - phi_tot: summed phase retardation in A [rad]


    Parameters
    ----------
    qpi: qpimage.QPImage
        QPI data
    center: tuble (x,y)
        Center of the disk region [px]
    r: float
        Radius of the disk region [m]
    wavelength: float
        The wavelength of the light in pixels
    alpha: float
        Refraction increment [m³/kg]


    Returns
    -------
    dry_mass: float
        The dry mass of the object [pg]
    """
    image = qpi.pha
    radius = r / qpi["pixel size"] * rad_fact
    wavelength = qpi["wavelength"]
    sx, sy = qpi.shape
    x = np.arange(sx).reshape(-1, 1)
    y = np.arange(sy).reshape(1, -1)
    discsq = ((x - center[0])**2 + (y - center[1])**2)
    area = discsq < radius**2
    phi_tot = np.sum(image[area])
    # compute dry mass
    pxarea = qpi["pixel size"]**2
    # [kg]
    m = wavelength / (2 * np.pi * alpha) * phi_tot * pxarea
    # [kg] -> [pg]
    m_pg = m * 1e15
    return m_pg
