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
                    "rel_dry_mass_pg": compute_relative_dry_mass(
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


def compute_sphere_dry_mass(radius, center, index, alpha=.2):
    dm_sphere = 4/3 * np.pi * radius**3 * (index - 1.333) / alpha
    return dm_sphere
    

def compute_relative_dry_mass(qpi, radius, center, alpha=.2, rad_fact=1.2):
    """Compute dry mass of a circular area in QPI

    The dry mass is computed with

    m = lambda / (2*PI*alpha) * phi_tot * deltaA

    with the vacuum wavelength `lambda`, the total phase
    retardation in the area of interest `phi_tot`, and the pixel
    area `deltaA`.

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
        does not have an effect after a critical value
    
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
